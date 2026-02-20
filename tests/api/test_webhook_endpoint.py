"""Test Webhooks"""

import hashlib
import hmac
import json
from csv import DictReader
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from django.test import LiveServerTestCase, override_settings
from rest_framework import status

from config.settings import base
from ddionrails.data.models.variable import Variable
from ddionrails.imports.management.commands.update import update_single_study
from ddionrails.imports.manager import StudyImportManager
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.studies.models import Study
from ddionrails.workspace.models.basket_variable import BasketVariable
from tests.conftest import PatchDict
from tests.imports.management_commands.test_update import IMPORT_PATH

from ..workspace.factories import BasketFactory


@override_settings(DEBUG=True)
@pytest.mark.usefixtures("mock_import_path")
class WebhookEndpointTests(  # pylint:disable=too-many-instance-attributes
    LiveServerTestCase
):
    """Test Webhook for updating studies"""

    mock_import_path_arguments: PatchDict

    def _set_up_webhook_content(self):
        repo_url_part = f"github.com/paneldata/test{self.study.name}"
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

    def setUp(self):
        with open(
            IMPORT_PATH.joinpath("variables.csv"), encoding="utf8"
        ) as variables_file:

            study_name = next(DictReader(variables_file))["study_name"]
        self.study, _ = Study.objects.get_or_create(name=study_name)
        self.study.save()
        self._set_up_webhook_content()
        self.study.save()

        self._update_study()

        self.basket = BasketFactory(name="test_basket")
        self.basket.study = self.study
        self.basket_variable = BasketVariable()
        self.basket_variable.basket = self.basket
        self.basket_variable.variable = Variable.objects.filter(
            dataset__study=self.study
        ).first()
        self.basket_variable_variable_name = self.basket_variable.variable.name
        self.basket_variable.save()

    def test_webhook_post_successful(self):
        """Test correct post request."""

        with patch("ddionrails.api.views.webhooks.run_import_on_redis") as runner_mock:
            with patch("ddionrails.api.views.webhooks.enqueue") as queue_mock:
                response = self.client.post(
                    self.url,
                    data=self.github_data,
                    content_type="application/json",
                    headers=self.github_headers,
                )
                queue_mock.assert_called_with(runner_mock, self.study.name)

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

        with patch("ddionrails.api.views.webhooks.enqueue") as queue_mock:
            response = self.client.post(
                self.url,
                data=data,
                content_type="application/json",
                headers=github_headers,
            )
            queue_mock.assert_not_called()

        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_webhook_post_develop_branch(self):
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

        with patch("ddionrails.api.views.webhooks.run_import_on_redis") as runner_mock:
            with patch.object(base, "SERVER_TYPE", "staging"):
                with patch("ddionrails.api.views.webhooks.enqueue") as queue_mock:
                    response = self.client.post(
                        self.url,
                        data=data,
                        content_type="application/json",
                        headers=github_headers,
                    )
                    queue_mock.assert_called_with(runner_mock, self.study.name)

        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_basket_preservation(self):
        """Check if basket variables are properly recovered from backup"""
        instrument = Instrument.objects.filter(study=self.study).first()
        instrument_name = instrument.name
        instrument.delete()
        self.study.import_path = lambda *args: Path(
            self.mock_import_path_arguments["return_value"]
        )
        self.study.save()

        # All the patching start
        tmp_backup = TemporaryDirectory()  # pylint: disable=consider-using-with

        backup_dir_helpers_patch = patch(
            "ddionrails.api.helpers.BACKUP_DIR", Path(tmp_backup.name)
        )
        queue_mock_helpers_patch = patch("ddionrails.api.helpers.enqueue")
        queue_mock_webhook_patch = patch("ddionrails.api.views.webhooks.enqueue")
        set_up_repo_patch = patch(
            "ddionrails.imports.management.commands.update.set_up_repo"
        )
        update_function_patch = patch("ddionrails.api.helpers.update_single_study")

        backup_dir_helpers_patch.start()
        queue_mock_helpers = queue_mock_helpers_patch.start()
        queue_mock_webhook = queue_mock_webhook_patch.start()
        set_up_repo_patch.start()
        update_function_mock = update_function_patch.start()

        queue_mock_helpers.side_effect = self._enqueue
        queue_mock_webhook.side_effect = self._enqueue
        update_function_mock.side_effect = lambda *_, **__: self._update_study()
        # All the patching end

        with override_settings(BACKUP_DIR=Path(tmp_backup.name)):
            self.client.post(
                self.url,
                data=self.github_data,
                content_type="application/json",
                headers=self.github_headers,
            )

        # Tear down all the patching start
        backup_dir_helpers_patch.stop()
        queue_mock_helpers.stop()
        queue_mock_webhook.stop()
        set_up_repo_patch.stop()
        update_function_patch.stop()

        tmp_backup.cleanup()
        # Tear down all the patching end

        # Indirectly make sure the import actually happened
        self.assertTrue(Instrument.objects.filter(name=instrument_name).exists())

        basket_variable_variable = Variable.objects.get(
            name=self.basket_variable_variable_name
        )
        self.assertTrue(
            BasketVariable.objects.filter(variable=basket_variable_variable).exists()
        )

    def _enqueue(self, function, *args):
        function(*args)

    def _update_study(self):
        with patch(
            "ddionrails.imports.management.commands.update.enqueue"
        ) as mock_enqueue:
            mock_enqueue.side_effect = self._enqueue
            with patch(**self.mock_import_path_arguments):
                with patch("ddionrails.imports.management.commands.update.set_up_repo"):
                    manager = StudyImportManager(self.study, redis=False)
                    update_single_study(self.study, False, (), "", manager=manager)
