# -*- coding: utf-8 -*-

""" "Add" management command for ddionrails project """

import djclick as click
from django.db.utils import IntegrityError

from ddionrails.studies.models import Study


@click.command()
@click.argument("study_name")
@click.argument("repo_url")
def command(study_name: str, repo_url: str) -> None:
    """ Add a study to the database """
    try:
        Study.objects.get(name=study_name)
        click.secho(f'Study name "{study_name}" is already taken.', fg="red")
        exit(1)
    except Study.DoesNotExist:
        try:
            Study.objects.create(name=study_name, repo=repo_url)
            click.secho(
                f'Study "{study_name}" succesfully added to database.', fg="green"
            )
        except IntegrityError as error:
            click.secho(error, fg="red")
