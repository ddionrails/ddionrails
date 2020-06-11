# -*- coding: utf-8 -*-

""" "Update" management command for ddionrails project """
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study


class Command(BaseCommand):
    """Update the data of a study from its associated git repository."""

    help = """Update command

        This command is used to update study metadata in ddionrails.

        \b
        Arguments:
            study_name: The name of a study (optional).
            entity: One or more entities to be updated (optional).
            local: Set this flag to suppress updating from GitHub (optional).
            filename: The filename of a single file, only used in combination
                      with a single 'entity' (optional).
        """

    def add_arguments(self, parser):
        parser.add_argument("study_name", nargs="?", type=str, default="all")
        parser.add_argument("entity", nargs="*", default=set())
        parser.add_argument(
            "-l",
            "--local",
            action="store_true",
            help="Do not try to update data from remote repository.",
            default=False,
        )
        parser.add_argument("-f", "--filename", nargs="?", type=Path, default=None)
        parser.add_argument(
            "-c",
            "--clean-import",
            action="store_true",
            help="Remove study content before import.",
            default=False,
        )
        parser.add_argument(
            "-r",
            "--no-redis",
            action="store_true",
            help="Do not queue jobs with redis.",
            default=False,
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        study_name = options["study_name"]
        entity = set(options["entity"])
        local = options["local"]
        filename = options["filename"]
        clean_import = options["clean_import"]
        redis = not options["no_redis"]

        # if no study_name is given, update all studies
        if study_name == "all":
            self.log_success("Updating all studies")
            update_all_studies_completely(local, clean_import, redis=redis)
            sys.exit(0)

        # if study_name is given, select study from database or exit
        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            self.log_error(f'Study "{study_name}" does not exist.')
            sys.exit(1)

        # if one or more entities are given, validate all are available
        manager = StudyImportManager(study, redis=redis)
        for single_entity in entity:
            if single_entity not in manager.import_order:
                self.log_error(f'Entity "{single_entity}" does not exist.')
                sys.exit(1)

        # if filename is given, validate that entity is "datasets.json" or "instruments"
        if filename and not entity.intersection({"datasets.json", "instruments"}):
            out = ", ".join(entity.intersection({"datasets.json", "instruments"}))
            self.log_error(
                f'Support for single file import not available for entity "{out}".'
            )
            sys.exit(1)

        update_single_study(
            study, local, tuple(entity), filename, clean_import, manager=manager
        )

        # Populate the search index from the database (indexes everything)
        sys.exit(0)

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.ERROR(message))


def update_study_partial(manager: StudyImportManager, entity: tuple):
    """ Update only selected entitites for study """
    for single_entity in entity:
        manager.import_single_entity(single_entity)


# Maybe replace study arg with manager arg in future refactor
def update_single_study(  # pylint: disable=R0913
    study: Study,
    local: bool,
    entity: tuple = None,
    filename: str = None,
    clean_import=False,
    manager: StudyImportManager = None,
) -> None:
    """ Update a single study """
    if clean_import:
        study.delete()
        study.save()
    if not manager:
        StudyImportManager(study)
    if not local:
        manager.update_repo()
    if not entity:
        manager.import_all_entities()
    elif filename:
        manager.import_single_entity(entity[0], filename)
    else:
        update_study_partial(manager, entity)


def update_all_studies_completely(local: bool, clean_import=False, redis=True) -> None:
    """ Update all studies in the database """
    for study in Study.objects.all():
        manager = StudyImportManager(study, redis=redis)
        update_single_study(study, local, clean_import=clean_import, manager=manager)
        del manager
