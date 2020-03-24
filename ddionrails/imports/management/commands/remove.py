# -*- coding: utf-8 -*-

""" "Remove" management command for ddionrails project """

import sys

from django.core.management.base import BaseCommand

from ddionrails.data.models import Variable
from ddionrails.studies.models import Study


class Command(BaseCommand):
    """Remove study entity from database via management command."""

    help = "Remove a study from the database."

    def add_arguments(self, parser):
        parser.add_argument("study_name", type=str)
        parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            help="Do not prompt for confirmation.",
            default=False,
        )

    def handle(self, *args, **options):
        study_name = options["study_name"]
        force = options["yes"]
        study = None
        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            self.log_error(f'Study "{study_name}" does not exist.')
            sys.exit(1)
        if not force:
            self.summary(study)
            confirmed = ""
            while confirmed not in list("yYnN"):
                # Bandit should ignore this. We do not use python2
                confirmed = input(  # nosec
                    f"Do you want to delete study {study_name}? [y/n]"
                )
            if confirmed and confirmed in "Yy":
                self.remove_from_database(study)
                return None
            self.log_success(f'Study "{study_name}" was not removed.')
            sys.exit(0)
        self.remove_from_database(study)
        return None

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.ERROR(message))

    def log_warning(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.WARNING(message))

    def summary(self, study: Study) -> None:
        """ Display a summary of all related objects that are going to be removed """

        counts = dict(
            datasets=study.datasets.count(),
            instruments=study.instruments.count(),
            periods=study.periods.count(),
            baskets=study.baskets.count(),
            variables=Variable.objects.filter(dataset__study=study).count(),
            publications=study.publications.count(),
        )
        positive_counts = {
            related_object: count for related_object, count in counts.items() if count > 0
        }
        if positive_counts:
            self.log_warning(f"The following related objects are going to be deleted:")
            for related_object, count in positive_counts.items():
                self.log_warning(f"# {related_object}: {count}")

    def remove_from_database(self, study: Study) -> None:
        """ Remove the study and all related objects from the database """

        study.delete()
        self.log_success(f'Study "{study.name}" succesfully removed from database.')
