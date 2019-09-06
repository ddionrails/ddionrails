# -*- coding: utf-8 -*-

""" Manager classes for imports in ddionrails project """

import logging
import shutil
from collections import OrderedDict
from typing import List

import django_rq
import git
from django.conf import settings
from git import InvalidGitRepositoryError, NoSuchPathError

from ddionrails.studies.models import Study

from . import importers

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


class Repository:
    """ A helper class to handle git related activities """

    def __init__(self, study_or_system) -> None:
        self.study_or_system = study_or_system
        self.name = study_or_system.name
        self.link = study_or_system.repo_url()
        self.path = settings.IMPORT_REPO_PATH.joinpath(self.name)
        try:
            self.repo = git.Repo(self.path)
        except (NoSuchPathError, InvalidGitRepositoryError):
            self.repo = None

    def set_branch(self, branch: str = settings.IMPORT_BRANCH) -> None:
        """ Checkout a branch """
        self.repo.git.checkout(branch)

    def pull_or_clone(self) -> None:
        """ Clones a repository from remote if it does not exist yet,
            otherwise pull
        """
        if self.path.exists() and self.repo is not None:
            print(f'Pulling "{self.name}" from "{self.link}"')
            self.repo.remotes.origin.pull()
        else:
            print(f'Cloning "{self.name}" from "{self.link}"')
            self.repo = git.Repo.clone_from(
                self.link, self.path, branch=settings.IMPORT_BRANCH, depth=1
            )

    def set_commit_id(self) -> None:
        """ Save the current commit hash inside the database

        Saves to the database field "current_commit" of study or system
        """
        self.study_or_system.current_commit = str(self.repo.head.commit)
        self.study_or_system.save()

    def is_import_required(self) -> bool:
        """ Returns True if the "current_commit" in the database differs from HEAD
            False otherwise
        """
        return self.study_or_system.current_commit != str(self.repo.head.commit)

    def list_changed_files(self) -> List:
        """ Returns a list of changed files since the "current_commit" in the database """
        diff = self.repo.git.diff(
            self.study_or_system.current_commit,
            "--",
            settings.IMPORT_SUB_DIRECTORY,
            name_only=True,
        )
        return diff.split()

    def list_all_files(self) -> List:
        """ Returns a list of all files in the "import_path" """
        return [
            file
            for file in sorted(self.study_or_system.import_path().glob("**/*"))
            if file.is_file()
        ]

    def import_list(self, import_all: bool = False) -> List:
        """ Returns a list of files to be imported """
        if import_all:
            return self.list_all_files()

        return self.list_changed_files()


class SystemImportManager:  # pylint: disable=too-few-public-methods
    """Import the files from the system repository."""

    def __init__(self, system):
        self.system = system
        self.repo = Repository(system)

    def run_import(self):
        """
        Run the system import.
        """
        import_path = self.system.import_path()
        studies_file = import_path.joinpath("studies.csv")
        importers.import_studies(studies_file)

        # Copy background image to static/
        image_file = import_path.joinpath("background.png")
        shutil.copy(image_file, "static/")
        self.repo.set_commit_id()


# Todo: Document StudyImportManager of ddionrails.imports.manager pylint: disable=fixme
class StudyImportManager:
    def __init__(self, study: Study):
        self.study = study
        self.repo = Repository(study)
        self.import_path = study.import_path()
        self.import_order = OrderedDict(
            {
                "study": (
                    importers.import_study_description,
                    self.import_path.glob("study.md"),
                ),
                "topics.csv": (
                    importers.import_topics_csv,
                    self.import_path.glob("topics.csv"),
                ),
                "topics.json": (
                    importers.import_topics_json,
                    self.import_path.glob("topics.json"),
                ),
                "concepts": (
                    importers.import_concepts,
                    self.import_path.glob("concepts.csv"),
                ),
                "analysis_units": (
                    importers.import_analysis_units,
                    self.import_path.glob("analysis_units.csv"),
                ),
                "periods": (
                    importers.import_periods,
                    self.import_path.glob("periods.csv"),
                ),
                "conceptual_datasets": (
                    importers.import_conceptual_datasets,
                    self.import_path.glob("conceptual_datasets.csv"),
                ),
                "instruments": (
                    importers.import_instruments,
                    self.import_path.glob("instruments.csv"),
                ),
                "questions": (
                    importers.import_questions,
                    self.import_path.glob("instruments/*.json"),
                ),
                "datasets.csv": (
                    importers.import_datasets_csv,
                    self.import_path.glob("datasets.csv"),
                ),
                "datasets.json": (
                    importers.import_datasets_json,
                    self.import_path.glob("datasets/*.json"),
                ),
                "variables": (
                    importers.import_variables,
                    self.import_path.glob("variables.csv"),
                ),
                "questions_variables": (
                    importers.import_questions_variables,
                    self.import_path.glob("questions_variables.csv"),
                ),
                "concepts_questions": (
                    importers.import_concepts_questions,
                    self.import_path.glob("concepts_questions.csv"),
                ),
                "transformations": (
                    importers.import_transformations,
                    self.import_path.glob("transformations.csv"),
                ),
                "attachments": (
                    importers.import_attachments,
                    self.import_path.glob("attachments.csv"),
                ),
                "publications": (
                    importers.import_publications,
                    self.import_path.glob("publications.csv"),
                ),
            }
        )

    def update_repo(self):
        """ `git pull` changes and update current commit """

        self.repo.pull_or_clone()
        self.repo.set_commit_id()

    def import_single_entity(self, entity: str, filename: str = None):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_single_entity("study")
        manager.import_single_entity("periods")
        manager.import_single_entity("instruments", "instruments/some-instrument.json")

        """
        LOGGER.info('Study "%s" starts import of entity: "%s"', self.study.name, entity)
        import_function, default_file_path = self.import_order.get(entity)

        # import with custom file path/name
        if filename:
            default_file_path = self.import_path.glob(filename)
        default_file_path = [_file for _file in default_file_path]

        if not default_file_path:
            LOGGER.warning(
                'Study "%s" has no file for the "%s" import.', self.study.name, entity
            )

        for file in sorted(default_file_path):
            if file.name == "topics.json":
                django_rq.enqueue(import_function, file, study=self.study)
            else:
                django_rq.enqueue(import_function, file)
            LOGGER.info(
                'Study "%s" starts import of file: "%s"', self.study.name, file.name
            )

    def import_all_entities(self):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_all_entities()

        """
        LOGGER.info('Study "%s" starts importing of all entities', self.study.name)
        for entity in self.import_order.keys():
            self.import_single_entity(entity)
