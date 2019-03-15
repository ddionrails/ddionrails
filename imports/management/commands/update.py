from pathlib import Path

from django.conf import settings

import djclick as click
from git import Repo
from studies.models import Study


def update_study(study):
    repo_dir = Path(settings.IMPORT_REPO_PATH) / study.name
    if repo_dir.exists():
        print("pulling")
        repo = Repo(repo_dir)
        repo.remotes.origin.pull(depth=1)
    else:
        print("cloning")
        Repo.clone_from(study.repo_url(), repo_dir, depth=1)


@click.command()
@click.option("-s", "--study", "study_name", default=False)
@click.option("-a", "--all", "_all", default=False, is_flag=True)
def command(study_name, _all):
    if _all:
        for study in Study.objects.all():
            update_study(study)
    elif study_name:
        try:
            study = Study.objects.get(name=study_name)
            update_study(study)
        except Exception as e:
            print(e)
            print(study)
    else:
        print("Please enter a valid study name")
