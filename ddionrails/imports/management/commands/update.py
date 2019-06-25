# -*- coding: utf-8 -*-

""" "Update" management command for ddionrails project """

import djclick as click

from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study


@click.command()
@click.option("-s", "--study", "study_name", default="", help="Update a single study")
@click.option(
    "-a", "--all", "_all", default=False, is_flag=True, help="Update all studies"
)
def command(study_name: str, _all: bool) -> None:
    """ This management command updates
        a single study selected from the database by "study_name"
        example usage:
            python manage.py update -s some-study
            python manage.py update --study some-study
        or all studies if "_all" is True
        example usage:
            python manage.py update -a
            python manage.py update --all
    """

    if _all:
        # Update all studies
        for study in Study.objects.all():
            manager = StudyImportManager(study)
            manager.update_repo()
    elif study_name:
        # Update single study
        try:
            study = Study.objects.get(name=study_name)
            manager = StudyImportManager(study)
            manager.update_repo()
            click.secho(f'Study data for "{study_name}" succesfully updated.', fg="green")
        except Study.DoesNotExist:
            click.secho(f'Study "{study_name}" does not exist.', fg="red")
            exit(1)
    else:
        click.secho("Please enter a study name.", fg="red")
        exit(1)
