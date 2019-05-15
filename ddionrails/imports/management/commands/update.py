# -*- coding: utf-8 -*-
""" Update management command for ddionrails project """

import pathlib

import djclick as click
import git
from django.conf import settings

from ddionrails.studies.models import Study


def update_study(study: Study) -> None:
    """ Clone a study's git repository with --depth=1
        or pull changes if git repository has already been cloned.

        The path to the git repository /repositories is set via the
        settings.IMPORT_REPO_PATH variable.
    """
    repository_directory = pathlib.Path(settings.IMPORT_REPO_PATH) / study.name
    if repository_directory.exists():
        print(f'Pulling "{study.name}" from "{study.repo_url()}"')
        repo = git.Repo(repository_directory)
        repo.remotes.origin.pull()
    else:
        print(f'Cloning "{study.name}" from "{study.repo_url()}"')
        git.Repo.clone_from(study.repo_url(), repository_directory, depth=1)


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
        for study in Study.objects.all():
            update_study(study)
    elif study_name:
        try:
            study = Study.objects.get(name=study_name)
            update_study(study)
        except Study.DoesNotExist:
            print(f'Study "{study_name}" does not exist.')
    else:
        print("Please enter a valid study name")
