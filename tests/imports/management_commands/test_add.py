# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for "add" management command for ddionrails project"""

from contextlib import redirect_stdout
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from ddionrails.studies.models import Study
from tests.model_factories import StudyFactory


class TestAdd(TestCase):

    def test_add_command_creates_study_object(self):
        """Test add management command creates a study"""
        self.assertEqual(0, Study.objects.count())
        study_name = "some-study"
        repo_url = "some-repo-url"
        call_command("add", study_name, repo_url)
        self.assertEqual(1, Study.objects.count())
        study = Study.objects.first()
        self.assertEqual(study_name, study.name)
        self.assertEqual(repo_url, study.repo)

    def test_add_command_displays_help(self):
        """Test add management command displays help with "-h" and "--help" """
        for option in ["-h", "--help"]:
            buffer = StringIO()
            with redirect_stdout(buffer):
                with self.assertRaises(SystemExit):
                    call_command("add", option)
                self.assertRegex(buffer.getvalue(), ".*usage:.*-h.*")

    def test_add_command_without_study_name(self):
        """Test add management command displays "missing argument" message"""
        with self.assertRaisesRegex(
            CommandError, ".*arguments are required: study_name.*"
        ):
            call_command("add")

    def test_add_command_without_repo_url(self):
        """Test add management command displays "missing argument" message"""
        with self.assertRaisesRegex(CommandError, ".*arguments are required: repo_url.*"):
            call_command("add", "some-study")

    def test_add_command_with_existing_study_name(self):
        """Test add management command with existing study name"""
        study = StudyFactory()
        self.assertEqual(1, Study.objects.count())
        study_name = study.name
        repo_url = study.repo
        with self.assertRaises(SystemExit):
            try:
                call_command("add", study_name, repo_url)
            except SystemExit as exit_error:
                self.assertEqual(1, exit_error.code)
                raise SystemExit()
        self.assertEqual(1, Study.objects.count())
