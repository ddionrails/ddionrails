# -*- coding: utf-8 -*-

""" "Update" management command for ddionrails project """

import djclick as click

from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study


def update_study_partial(manager: StudyImportManager, entity: tuple):
    """ Update only selected entitites for study """
    for single_entity in entity:
        manager.import_single_entity(single_entity)


def update_single_study(
    study: Study, local: bool, entity: tuple = None, filename: str = None
) -> None:
    """ Update a single study """
    manager = StudyImportManager(study)
    if not local:
        manager.update_repo()
    if not entity:
        manager.import_all_entities()
    elif filename:
        manager.import_single_entity(entity[0], filename)
    else:
        update_study_partial(manager, entity)


def update_all_studies_completely(local: bool) -> None:
    """ Update all studies in the database """
    click.secho(f"Updating all studies", fg="green")
    for study in Study.objects.all():
        update_single_study(study, local)


@click.command()
@click.argument("study_name", nargs=1, required=False)
@click.argument("entity", nargs=-1)
@click.option(
    "-l",
    "--local",
    default=False,
    is_flag=True,
    help="Set this flag to suppress updating from GitHub (local import)",
)
@click.option(
    "-f",
    "--filename",
    type=click.Path(exists=True),
    help="Filename of a single file to be imported, only used in combination with a single 'entity'",
)
def command(study_name: str, entity: tuple, local: bool, filename: str) -> None:
    """Update command

    This command is used to update study metadata in ddionrails.

    \b
    Arguments:
        study_name: The name of a study (optional).
        entity: One or more entities to be updated (optional).
        local: Set this flag to suppress updating from GitHub (optional).
        filename: The filename of a single file, only used in combination with a single 'entity' (optional).
    """

    # if no study_name is given, update all studies
    if study_name is None:
        update_all_studies_completely(local)
        exit(0)

    # if study_name is given, select study from database or exit
    try:
        study = Study.objects.get(name=study_name)
    except Study.DoesNotExist:
        click.secho(f'Study "{study_name}" does not exist.', fg="red")
        exit(1)

    # if one or more entities are given, validate all are available
    manager = StudyImportManager(study)
    for single_entity in entity:
        if single_entity not in manager.import_order:
            click.secho(f'Entity "{single_entity}" does not exist.', fg="red")
            exit(1)

    # if filename is given, validate that entity is "datasets.json" or "instruments"
    if filename and entity[0] not in {"datasets.json", "instruments"}:
        click.secho(
            f'Support for single file import not available for entity "{entity[0]}".',
            fg="red",
        )
        exit(1)

    update_single_study(study, local, entity, filename)
    exit(0)


# remove "verbosity", "settings", "pythonpath", "traceback", "color" options from django-click
command.params = command.params[:2] + command.params[7:]
