import djclick as click
from django.db.utils import IntegrityError

from config import Study


@click.command()
@click.argument("study_name")
@click.argument("repo_url")
def command(study_name: str, repo_url: str):
    try:
        Study.objects.create(name=study_name, repo=repo_url)
    except IntegrityError as e:
        print(e, study_name)
