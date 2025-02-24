"""Tools to handle git related actions"""

from pathlib import Path
from shutil import rmtree

from django.conf import settings
from git import Repo

from ddionrails.studies.models import Study


# TODO: Add unittests pylint: disable=fixme
def clean_repo_url(url: str) -> str:
    """Remove potential protocol and .git ending"""
    if url.startswith("http"):
        if url.startswith("https://"):
            url = url[8:]
        else:
            url = url[7:]
    if url.endswith(".git"):
        url = url[:-4]

    return url


def set_up_repo(study: Study) -> Path:
    """Initialize repo or get it to desired current state"""
    repo_base_path = Path(settings.IMPORT_REPO_PATH)
    study_repo_path = repo_base_path.joinpath(study.name)

    # Can't pull with shallow repo so we delete and clone most current as shallow.
    # We skip this when repo is pinned and current since full history pull is slow.
    if study_repo_path.exists():
        repo = Repo(study_repo_path)
        if study.pin_reference and study.current_commit == repo.head.object.hexsha:
            print("Repository is pinned and current.")
            return study_repo_path
        rmtree(study_repo_path)

    if study.pin_reference:
        Repo.clone_from(url=study.repo_url(), to_path=study_repo_path)
        repo = Repo(study_repo_path)
        repo.git.checkout(study.pin_reference)
        study.current_commit = repo.head.object.hexsha
        study.save()
        return study_repo_path

    Repo.clone_from(url=study.repo_url(), to_path=study_repo_path, depth=1)

    return study_repo_path
