"""Test Webhooks"""

import hashlib
import hmac
import json
from unittest.mock import patch

from django.test import LiveServerTestCase, override_settings
from rest_framework import status

from ddionrails.studies.models import Study


@override_settings(DEBUG=True)
class WebhookEndpointTests(LiveServerTestCase):
    """Test Webhook for updating studies"""

    def setUp(self):
        self.study = Study()
        self.study.name = "test"
        repo_url_part = "github.com/paneldata/test"
        self.study.repo = repo_url_part
        self.webhook_key = (
            "756825ea0eb2514fc211225cce999b9a37710b7d7661c32c77f4409c9b021e23"
        )
        self.study.webhook_secret = self.webhook_key
        self.url = "/api/webhooks/github/"

        # Simulate a minimal GitHub webhook payload (push event example)
        self.github_data = {
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "octocat/Hello-World",
                "html_url": f"https://{repo_url_part}",
            },
            "pusher": {"name": "octocat", "email": "octocat@github.com"},
        }

        self.encoding = "utf-8"

        self.digest = hmac.new(
            self.webhook_key.encode(self.encoding),
            msg=json.dumps(self.github_data).encode(self.encoding),
            digestmod=hashlib.sha256,
        ).hexdigest()

        self.github_headers = {
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "123e4567-e89b-12d3-a456-426614174000",
            "User-Agent": "GitHub-Hookshot/1.0",
            "CONTENT_TYPE": "application/json",
            "X-Hub-Signature-256": f"sha256={self.digest}",
        }
        self.study.save()

    def test_webhook_post_successful(self):
        """Test correct post request."""
        with patch("ddionrails.api.views.webhooks.StudyImportManager") as manager_mock:
            with patch("ddionrails.api.views.webhooks.update_single_study") as mock:
                response = self.client.post(
                    self.url,
                    data=self.github_data,
                    content_type="application/json",
                    headers=self.github_headers,
                )
                manager_mock.assert_called_with(self.study, redis=True)
                mock.assert_called_with(
                    self.study, local=False, clean_import=True, manager=manager_mock()
                )

        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_webhook_post_different_branch(self):
        """Test post request for non `default` branch"""
        data = self.github_data.copy()
        data["ref"] = "refs/head/develop"
        digest = hmac.new(
            self.webhook_key.encode(self.encoding),
            msg=json.dumps(data).encode(self.encoding),
            digestmod=hashlib.sha256,
        ).hexdigest()

        github_headers = self.github_headers.copy()
        github_headers["X-Hub-Signature-256"] = f"sha256={digest}"

        with patch("ddionrails.api.views.webhooks.StudyImportManager") as manager_mock:
            with patch("ddionrails.api.views.webhooks.update_single_study") as mock:
                response = self.client.post(
                    self.url,
                    data=data,
                    content_type="application/json",
                    headers=github_headers,
                )
                manager_mock.assert_not_called()
                mock.assert_not_called()

        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
