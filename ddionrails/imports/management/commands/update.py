# -*- coding: utf-8 -*-

""" "Update" management command for ddionrails project """
import sys
from pathlib import Path

from django.core.cache import caches
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_rq.queues import enqueue

from ddionrails.imports.git_repos import set_up_repo
from ddionrails.imports.helpers import clear_caches
from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable


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

    def handle(self, *_, **options):
        success, error = update(options)

        if error:
            self.log_error(error)
            sys.exit(1)
        if success:
            self.log_success(success)
        sys.exit(0)

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.ERROR(message))


def update_study_partial(manager: StudyImportManager, entity: tuple):
    """Update only selected entities for study"""
    for single_entity in entity:
        manager.import_single_entity(single_entity)


def update(options) -> tuple[str | None, str | None]:
    """Update a study."""
    study_name = options["study_name"]
    entity = options["entity"]
    if isinstance(entity, str):
        entity = {entity}
    else:
        entity = set(entity)
    local = options["local"]
    filename = options["filename"]
    clean_import = options["clean_import"]
    redis = not options["no_redis"]

    # if no study_name is given, update all studies
    if study_name == "all":
        update_all_studies_completely(local, clean_import, redis=redis)
        return ("Updating all studies", None)

    # if study_name is given, select study from database or exit
    try:
        study = Study.objects.get(name=study_name)
    except Study.DoesNotExist:
        return (None, f'Study "{study_name}" does not exist.')

    # if one or more entities are given, validate all are available
    manager = StudyImportManager(study, redis=redis)
    for single_entity in entity:
        if single_entity not in manager.import_order:
            return (None, f'Entity "{single_entity}" does not exist.')

    # if filename is given, validate that entity is "datasets.json" or "instruments"
    if filename and not entity.intersection({"datasets.json", "instruments.json"}):
        out = ", ".join(entity.intersection({"datasets.json", "instruments.json"}))
        return (None, f'Support for single file import not available for entity "{out}".')

    update_single_study(
        study, local, tuple(entity), filename, clean_import, manager=manager
    )

    if redis:
        enqueue(clear_caches)
    return ("Done", None)


def _clear_all_caches():
    caches["default"].clear()
    caches["instrument_api"].clear()
    caches["dataset_api"].clear()


# Maybe replace study arg with manager arg in future refactor
def update_single_study(  # pylint: disable=R0913
    study: Study,
    local: bool,
    entity: tuple = None,
    filename: str = None,
    clean_import=False,
    manager: StudyImportManager = None,
) -> None:
    """Update a single study"""
    backup_file = Path()
    if clean_import:
        backup_file = Basket.backup()
        study.delete()
        study.save()
    if not local:
        set_up_repo(study)
    if not entity:
        manager.import_all_entities()
    elif filename:
        manager.import_single_entity(entity[0], filename)
    else:
        update_study_partial(manager, entity)

    if backup_file.is_file():
        enqueue(call_command, "loaddata", backup_file)
        enqueue(BasketVariable.clean_basket_variables, study.name)
    enqueue(_clear_all_caches)


def update_all_studies_completely(local: bool, clean_import=False, redis=True) -> None:
    """Update all studies in the database"""
    for study in Study.objects.all():
        manager = StudyImportManager(study, redis=redis)
        update_single_study(study, local, clean_import=clean_import, manager=manager)
        del manager
