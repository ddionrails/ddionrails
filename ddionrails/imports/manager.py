# -*- coding: utf-8 -*-

""" Manager classes for imports in ddionrails project """

import csv
import logging
import shutil
import sys
from collections import OrderedDict
from pathlib import Path
from typing import List

import django_rq
import git
from django.conf import settings
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from ddionrails.base.models import System
from ddionrails.concepts.imports import (
    AnalysisUnitImport,
    ConceptImport,
    ConceptualDatasetImport,
    PeriodImport,
    TopicImport,
    TopicJsonImport,
)
from ddionrails.data.imports import (
    DatasetImport,
    DatasetJsonImport,
    TransformationImport,
    VariableImageImport,
    VariableImport,
)
from ddionrails.imports.helpers import patch_instruments
from ddionrails.instruments.imports import (
    ConceptQuestionImport,
    InstrumentImport,
    QuestionVariableImport,
)
from ddionrails.publications.imports import AttachmentImport, PublicationImport
from ddionrails.studies.imports import StudyDescriptionImport, StudyImport
from ddionrails.studies.models import Study

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
        """Save the current commit hash in the database."""
        self.study_or_system.current_commit = str(self.repo.head.commit)
        self.study_or_system.save()

    def is_import_required(self) -> bool:
        """Check if current commit is still the newest or of new import is required."""
        return self.study_or_system.current_commit != str(self.repo.head.commit)

    def list_changed_files(self) -> List:
        """Returns a list of changed files since the "current_commit" in the database."""
        diff = self.repo.git.diff(
            self.study_or_system.current_commit,
            "--",
            settings.IMPORT_SUB_DIRECTORY,
            name_only=True,
        )
        return diff.split()

    def list_all_files(self) -> List:
        """Returns a list of all files in the `import_path`."""
        return [
            file
            for file in sorted(self.study_or_system.import_path().glob("**/*"))
            if file.is_file()
        ]

    def import_list(self, import_all: bool = False) -> List:
        """Returns a list of files to be imported."""
        if import_all:
            return self.list_all_files()

        return self.list_changed_files()


class SystemImportManager:
    """Import the files from the system repository."""

    def __init__(self, system: System):
        self.system = system
        self.repo = Repository(system)

    def run_import(self):
        """Run the system import."""
        base_directory = self.system.import_path()
        studies_file = base_directory.joinpath("studies.csv")
        StudyImport.run_import(studies_file, self.system)

        # Copy background image to static/
        image_file = base_directory.joinpath("background.png")
        shutil.copy(image_file, "static/")
        self.repo.set_commit_id()


class StudyImportManager:
    def __init__(self, study: Study, redis: bool = True):
        self.study = study
        self.repo = Repository(study)
        self.base_dir = study.import_path()
        self._concepts_fixed = False
        self.redis = redis

        repositories_base_dir: Path = settings.IMPORT_REPO_PATH
        repository_dir = repositories_base_dir.joinpath(self.study.name)
        instruments_dir = repository_dir.joinpath("ddionrails/instruments")
        patch_instruments(repository_dir, instruments_dir)

        self.import_order = OrderedDict(
            {
                "topics.csv": (TopicImport, self.base_dir / "topics.csv"),
                "topics.json": (TopicJsonImport, self.base_dir / "topics.json"),
                "concepts": (ConceptImport, self.base_dir / "concepts.csv"),
                "analysis_units": (
                    AnalysisUnitImport,
                    self.base_dir / "analysis_units.csv",
                ),
                "periods": (PeriodImport, self.base_dir / "periods.csv"),
                "conceptual_datasets": (
                    ConceptualDatasetImport,
                    self.base_dir / "conceptual_datasets.csv",
                ),
                "instruments": (
                    InstrumentImport,
                    Path(self.base_dir / "instruments/").glob("*.json"),
                ),
                "datasets.json": (
                    DatasetJsonImport,
                    Path(self.base_dir / "datasets/").glob("*.json"),
                ),
                "datasets.csv": (DatasetImport, self.base_dir / "datasets.csv"),
                "variables": (VariableImport, self.base_dir / "variables.csv"),
                "questions_variables": (
                    QuestionVariableImport,
                    self.base_dir / "questions_variables.csv",
                ),
                "concepts_questions": (
                    ConceptQuestionImport,
                    self.base_dir / "concepts_questions.csv",
                ),
                "transformations": (
                    TransformationImport,
                    self.base_dir / "transformations.csv",
                ),
                "attachments": (AttachmentImport, self.base_dir / "attachments.csv"),
                "publications": (PublicationImport, self.base_dir / "publications.csv"),
                "study": (StudyDescriptionImport, self.base_dir / "study.md"),
            }
        )

    def fix_concepts_csv(self):
        """Add missing concepts, only present in the variable.csv, to the concepts.csv"""
        if self._concepts_fixed:
            return None
        concept_path = Path(self.import_order["concepts"][1])
        if not concept_path.exists():
            return None
        variable_path = self.import_order["variables"][1]
        with open(variable_path, "r") as variable_csv:
            variable_concepts = {
                row.get("concept", row.get("concept_name"))
                for row in csv.DictReader(variable_csv)
            }
        with open(concept_path, "r") as concepts_csv:
            _reader = csv.DictReader(concepts_csv)
            concept_csv_content = list(_reader)
            concept_fields = {field: "" for field in _reader.fieldnames}
            concepts = {row["name"] for row in concept_csv_content}
        orphaned_concepts = variable_concepts.difference(concepts)
        if "" in orphaned_concepts:
            orphaned_concepts.remove("")
        with open(concept_path, "w") as concepts_csv:
            writer = csv.DictWriter(concepts_csv, concept_fields.keys())
            writer.writeheader()
            for row in concept_csv_content:
                writer.writerow(row)
            for concept in orphaned_concepts:
                concept_fields["name"] = concept
                writer.writerow(concept_fields)
        self._concepts_fixed = True
        return None

    def update_repo(self):
        self.repo.pull_or_clone()
        self.repo.set_commit_id()

    def _execute(self, import_function, *args):
        if self.redis:
            django_rq.enqueue(import_function, *args)
        else:
            import_function(*args)

    def import_single_entity(self, entity: str, filename: str = None):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_single_entity("study")
        manager.import_single_entity("periods")
        manager.import_single_entity("instruments", "instruments/some-instrument.json")

        """
        if "concepts" in entity or "variables" in entity:
            self.fix_concepts_csv()
        LOGGER.info(f'Study "{self.study.name}" starts import of entity: "{entity}"')
        importer_class, default_file_path = self.import_order.get(entity)

        # import specific file
        if filename:
            file = self.base_dir / filename
            if file.is_file():
                LOGGER.info(
                    f'Study "{self.study.name}" starts import of file: "{file.name}"'
                )
                importer = importer_class(file, self.study)
                self._execute(importer.run_import, file, self.study)
            else:
                LOGGER.error(f'Study "{self.study.name}" has no file: "{file.name}"')
                sys.exit(1)
        else:

            # single file import
            if isinstance(default_file_path, Path):
                if default_file_path.is_file():
                    importer = importer_class(default_file_path, self.study)
                    self._execute(importer.run_import, default_file_path, self.study)
                else:
                    LOGGER.warning(
                        (
                            f'Study "{self.study.name}" '
                            f'has no file: "{default_file_path.name}"'
                        )
                    )

            # multiple files import, e.g. instruments, datasets
            else:

                for file in sorted(default_file_path):
                    LOGGER.info(
                        f'Study "{self.study.name}" starts import of file: "{file.name}"'
                    )
                    importer = importer_class(file, self.study)
                    self._execute(importer.run_import, file, self.study)

    def import_all_entities(self):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_all_entities()

        """
        LOGGER.info(f'Study "{self.study.name}" starts importing of all entities')
        for entity in self.import_order.keys():
            self.import_single_entity(entity)

        # VariableImageImport Patch
        variable_image_import = VariableImageImport(
            self.base_dir / "variables_images.csv"
        )
        if variable_image_import:
            self._execute(variable_image_import.image_import)
