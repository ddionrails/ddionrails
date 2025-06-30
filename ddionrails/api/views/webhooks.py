"""Handle WebHook requests"""

import hashlib
import hmac
import logging
from typing import Literal

from django_rq.queues import enqueue
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from config.settings import base
from ddionrails.api.helpers import run_import_on_redis
from ddionrails.studies.models import Study

logger = logging.getLogger(__name__)

MAIN_BRANCH_CANDIDATES: tuple[Literal["master"], Literal["main"]] = ("master", "main")
DEVELOP_BRANCH_CANDIDATES: tuple[
    Literal["develop"], Literal["development"], Literal["dev"]
] = ("develop", "development", "dev")


class WebhookView(ViewSet):
    """Handle WebHook requests"""

    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=["post", "get"])
    def github(self, request, *args, **kwargs):  # pylint: disable=unused-variable
        """Handle GitHub post requests"""
        signature = request.headers.get("X-Hub-Signature-256")
        payload: bytes = request.body

        post_data = request.data
        repo_url: str = post_data["repository"]["html_url"]
        if repo_url.startswith("https://"):
            repo_url = repo_url[8:]
        study = Study.objects.get(repo=repo_url)

        if not study:
            return Response(
                {"detail": "Invalid repository"}, status=status.HTTP_404_NOT_FOUND
            )

        if not self._verify_signature_github(payload, signature, study):
            return Response(
                {"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN
            )

        event = request.headers.get("X-GitHub-Event")
        data = request.data

        if event is None:
            logging.info("WEBHOOK: Received ping from webhook.")
            return Response({"detail": "Received"}, status=status.HTTP_200_OK)

        if event == "push":
            _handle_branch_verification(study, data)
            return Response({"detail": "Push event processed"}, status=status.HTTP_200_OK)

        return Response({"detail": "Unhandled event"}, status=status.HTTP_200_OK)

    def _verify_signature_github(self, payload, header_signature, study):
        """Verify signature for GitHub request"""
        if header_signature is None:
            return False

        secret = study.webhook_secret.encode("utf-8")
        if not secret:
            return False

        try:
            sha_name, signature = header_signature.split("=")
        except ValueError:
            return False

        if sha_name != "sha256":
            return False

        our_signature = hmac.new(
            secret, msg=payload, digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(our_signature, signature)


def _is_develop(push_reference: str) -> bool:
    return (
        any(push_reference.endswith(name) for name in DEVELOP_BRANCH_CANDIDATES)
        and base.SERVER_TYPE == "staging"
    )


def _is_main(push_reference: str) -> bool:
    return (
        any(push_reference.endswith(name) for name in MAIN_BRANCH_CANDIDATES)
        and base.SERVER_TYPE == "live"
    )


def _handle_branch_verification(study, data):
    repo = data.get("repository", {}).get("full_name", "unknown")
    logging.info("WEBHOOK: Received push to %s", repo)
    push_reference: str = data.get("ref", "")
    if _is_develop(push_reference) or _is_main(push_reference):
        logging.info("WEBHOOK: Updating %s", study.name)
        enqueue(run_import_on_redis, study.name)
        logging.info("WEBHOOK: Update queued")
        return None
    return None
