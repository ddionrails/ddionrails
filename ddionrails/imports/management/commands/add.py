# -*- coding: utf-8 -*-

""" "Add" management command for ddionrails project """

import sys

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from ddionrails.studies.models import Study


class Command(BaseCommand):
    """Add study entity via management command."""

    help = "Add a study to the database."

    def add_arguments(self, parser):
        parser.add_argument("study_name", type=str)
        parser.add_argument("repo_url", type=str)

    def handle(self, *args, **options):
        study_name: str = options["study_name"]
        repo_url: str = options["repo_url"]

        # Remove leading scheme part from url if present.
        if repo_url.startswith("http"):
            if repo_url.startswith("https://"):
                repo_url = repo_url[8:]
            else:
                repo_url = repo_url[7:]

        try:
            Study.objects.get(name=study_name)
            self.log_error(f'Study name "{study_name}" is already taken.')
            sys.exit(1)
        except Study.DoesNotExist:
            try:
                Study.objects.create(name=study_name, repo=repo_url)
                self.log_success(f'Study "{study_name}" successfully added to database.')
            except IntegrityError as error:
                self.log_error(str(error))

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.ERROR(message))
