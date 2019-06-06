# -*- coding: utf-8 -*-

""" "Remove" management command for ddionrails project """

import djclick as click
from click.exceptions import Abort

from ddionrails.data.models import Variable
from ddionrails.studies.models import Study


def summary(study: Study) -> None:
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
        click.secho(
            f"The following related objects are going to be deleted:", fg="yellow"
        )
        for related_object, count in positive_counts.items():
            click.secho(f"# {related_object}: {count}", fg="yellow")


def remove_from_database(study: Study) -> None:
    """ Remove the study and all related objects from the database """

    study.delete()
    click.secho(f'Study "{study.name}" succesfully removed from database.', fg="green")


@click.command()
@click.argument("study_name")
@click.option("-f", "--force", default=False, is_flag=True)
def command(study_name: str, force: bool) -> None:
    study = None
    try:
        study = Study.objects.get(name=study_name)
    except Study.DoesNotExist:
        click.secho(f'Study "{study_name}" does not exist.', fg="red")
        exit(1)
    if force is True:
        remove_from_database(study)
    else:
        try:
            summary(study)
            click.confirm("Do you want to continue?", abort=True)
            remove_from_database(study)
        except Abort:
            click.secho(f'Study "{study_name}" was not removed.', fg="green")
