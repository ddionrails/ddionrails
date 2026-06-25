# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for "remove" management command for ddionrails project"""

from io import StringIO
import sys
from unittest.mock import patch

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from ddionrails.studies.models import Study
from tests.model_factories import StudyFactory


class TestRemove(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.mocked_delete_patch = patch.object(Study, "delete")
        self.mocked_delete_method = self.mocked_delete_patch.start()
        self.old_stderr = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout
        return super().setUp()

    def tearDown(self) -> None:
        self.mocked_delete_patch.stop()
        sys.stderr = self.old_stderr
        return super().tearDown()

    def test_remove_command_without_study_name(self):
        """Test remove management command displays "missing argument" message"""
        with self.assertRaisesRegex(
            CommandError, "Error: the following arguments are required: study_name"
        ):
            call_command("remove")

    def test_remove_command_displays_help(self):
        """Test remove management command displays help with "-h" and "--help" """
        for option in ["-h", "--help"]:
            with self.assertRaises(SystemExit):
                call_command("remove", option)
            self.assertRegex(self.stdout.getvalue(), ".*usage:.*-h.*")

    def test_remove_command_with_non_existing_study(self):
        """Test remove management command displays "does not exist" message"""
        with patch("builtins.input", side_effect="Y"):
            try:
                call_command("remove", self.study.name)
            except SystemExit as exit_error:
                self.assertEqual(1, exit_error.code)
                self.assertIn(
                    f'Study "{self.study.name}" does not exist.', self.stdout.getvalue()
                )
                raise exit_error

    def test_remove_command_aborts(self):
        """Test remove management command aborts when given "N" as input"""
        study_name = self.study.name
        with patch("builtins.input", side_effect="N"):
            # command should sys.exit with exit code 0
            with self.assertRaisesRegex(SystemExit, "0"):
                try:
                    call_command("remove", study_name)
                except SystemExit as exit_error:
                    # command should log before exit
                    self.assertIn(
                        f'Study "{self.study.name}" was not removed.',
                        self.stdout.getvalue(),
                    )
                    raise exit_error
        # command should exit without removing study
        self.mocked_delete_method.assert_not_called()

    def test_remove_command_removes_study(self):
        """Test remove management command removes study when given "y" as input"""
        study_name = self.study.name

        with patch("builtins.input", side_effect="Y"):
            call_command("remove", study_name)
            self.assertEqual(
                f'Study "{study_name}" successfully removed from database.\n',
                self.stdout.getvalue(),
            )
        self.mocked_delete_method.assert_called_once()

    def test_remove_command_force_removes_study(self):
        for call, option in enumerate(["-y", "--yes"], start=1):
            stdout = StringIO()
            sys.stdout = stdout
            study = StudyFactory()
            study_name = study.name
            call_command("remove", option, study_name)
            self.assertEqual(
                f'Study "{study.name}" successfully removed from database.\n',
                stdout.getvalue(),
            )
            self.assertEqual(call, self.mocked_delete_method.call_count)
