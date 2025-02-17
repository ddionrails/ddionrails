# -*- coding: utf-8 -*-

""" Manager classes for imports in ddionrails project """

import csv
import logging
import shutil
import sys
from collections import OrderedDict
from inspect import isfunction
from pathlib import Path
from types import FunctionType
from typing import Any, List, Tuple

import django_rq
import git
from django.conf import settings
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from ddionrails.base.models import System
from ddionrails.concepts.imports import (
    AnalysisUnitImport,
    PeriodImport,
    TopicImport,
    TopicJsonImport,
    concept_import,
    conceptual_dataset_import,
)
from ddionrails.data.imports import (
    DatasetImport,
    DatasetJsonImport,
    TransformationImport,
    VariableImport,
    variables_images_import,
)
from ddionrails.instruments.imports import (
    concept_question_import,
    instrument_import,
    question_image_import,
    question_import,
    question_variable_import,
)
from ddionrails.publications.imports import AttachmentImport, PublicationImport
from ddionrails.studies.imports import StudyDescriptionImport, StudyImport
from ddionrails.studies.models import Study
from ddionrails.workspace.imports import script_metadata_import

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


class Repository:
    """A helper class to handle git related activities"""

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
        """Checkout a branch"""
        self.repo.git.checkout(branch)

    def pull_or_clone(self) -> None:
        """Clones or update the study repository."""
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
        if isinstance(self.study_or_system, System):
            return [
                settings.IMPORT_REPO_PATH.joinpath(
                    "system", settings.IMPORT_SUB_DIRECTORY
                )
            ]
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


def system_import_manager(system):
    """Import the files from the system repository."""

    repo = Repository(system)
    base_directory = settings.IMPORT_REPO_PATH.joinpath("system").joinpath(
        settings.IMPORT_SUB_DIRECTORY
    )
    studies_file = base_directory.joinpath("studies.csv")
    StudyImport.run_import(studies_file, system)

    # Copy background image to static/
    image_file = base_directory.joinpath("background.png")
    shutil.copy(image_file, "static/")
    repo.set_commit_id()


class StudyImportManager:
    """Manage the import of all study resources."""

    import_order: OrderedDict[str, Tuple[Any, Any]]

    def __init__(self, study: Study, redis: bool = True):
        self.study = study
        self.repo = Repository(study)
        self.base_dir = study.import_path()
        self._concepts_fixed = False
        self.redis = redis

        self.import_order = OrderedDict(
            {
                "study": (StudyDescriptionImport, self.base_dir / "study.md"),
                "topics.csv": (TopicImport, self.base_dir / "topics.csv"),
                "topics.json": (TopicJsonImport, self.base_dir / "topics.json"),
                "concepts": (concept_import, self.base_dir / "concepts.csv"),
                "analysis_units": (
                    AnalysisUnitImport,
                    self.base_dir / "analysis_units.csv",
                ),
                "periods": (PeriodImport, self.base_dir / "periods.csv"),
                "conceptual_datasets": (
                    conceptual_dataset_import,
                    self.base_dir / "conceptual_datasets.csv",
                ),
                "instruments.json": (
                    instrument_import.InstrumentImport,
                    Path(self.base_dir / "instruments/").glob("*.json"),
                ),
                "instruments": (
                    instrument_import.instrument_import,
                    Path(self.base_dir / "instruments.csv"),
                ),
                "questions": (
                    question_import.question_import,
                    self.base_dir / "questions.csv",
                ),
                "answers": (question_import.answer_import, self.base_dir / "answers.csv"),
                "answers_relations": (
                    question_import.answer_relation_import,
                    self.base_dir / "answers.csv",
                ),
                "datasets.csv": (DatasetImport, self.base_dir / "datasets.csv"),
                "datasets.json": (
                    DatasetJsonImport,
                    Path(self.base_dir / "datasets/").glob("*.json"),
                ),
                "variables": (VariableImport, self.base_dir / "variables.csv"),
                "questions_variables": (
                    question_variable_import.question_variable_import,
                    self.base_dir / "questions_variables.csv",
                ),
                "concepts_questions": (
                    concept_question_import.ConceptQuestionImport,
                    self.base_dir / "questions.csv",
                ),
                "transformations": (
                    TransformationImport,
                    self.base_dir / "transformations.csv",
                ),
                "attachments": (AttachmentImport, self.base_dir / "attachments.csv"),
                "publications": (PublicationImport, self.base_dir / "publications.csv"),
                "questions_images": (
                    question_image_import.questions_images_import,
                    self.base_dir.joinpath("questions_images.csv"),
                ),
                "variables_images": (
                    variables_images_import,
                    self.base_dir.joinpath("variables_images.csv"),
                ),
                "script_metadata": (
                    script_metadata_import,
                    self.base_dir.joinpath("script_metadata.csv"),
                ),
            }
        )

    def fix_concepts_csv(self):
        """Add missing concepts, only present in the variable.csv, to the concepts.csv"""
        if self._concepts_fixed:
            return None
        concept_path = Path(self.import_order["concepts"][1]).resolve()
        if not concept_path.exists():
            return None
        variable_path = Path(self.import_order["variables"][1]).resolve()
        with open(variable_path, "r", encoding="utf8") as variable_csv:
            variable_concepts = {
                row.get("concept", row.get("concept_name"))
                for row in csv.DictReader(variable_csv)
            }
        with open(concept_path, "r", encoding="utf8") as concepts_csv:
            _reader = csv.DictReader(concepts_csv)
            concept_csv_content = list(_reader)
            concept_fields = {field: "" for field in _reader.fieldnames}
            concepts = {row["name"] for row in concept_csv_content}
        orphaned_concepts = variable_concepts.difference(concepts)
        if "" in orphaned_concepts:
            orphaned_concepts.remove("")
        with open(concept_path, "w", encoding="utf8") as concepts_csv:
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
        "Update metadata git repository."
        self.repo.pull_or_clone()
        self.repo.set_commit_id()

    def _execute(self, import_function: FunctionType, *args):
        """Queue or call an import function."""
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
        self.__log_import_start(entity)
        importer_class, _default_files_path = self.import_order.get(entity)
        default_importer_files: Any
        if isinstance(_default_files_path, (str, Path)):
            default_importer_files = [_default_files_path]
        else:
            default_importer_files = list(_default_files_path)

        # import specific file
        if filename:
            file = self.base_dir.joinpath(filename)
            if file.is_file():
                self.__log_import_start(getattr(file, "name", ""))
                default_importer_files = [file]
            else:
                self.__log_import_fail(file)
                sys.exit(1)

        for file in default_importer_files:
            self.__log_import_start(getattr(file, "name", ""))
            if not file.is_file():  # type: ignore
                self.__log_import_fail(file)
                continue
            if isfunction(importer_class):
                importer = importer_class
            else:
                _importer = importer_class(file, self.study)
                importer = _importer.run_import
            self._execute(importer, file, self.study)

    def __log_import_start(self, file: str) -> None:
        LOGGER.info('Study "%s" starts import of: "%s"', self.study.name, file)

    def __log_import_fail(self, file: Path) -> None:
        LOGGER.error('Study "%s" has no file: "%s"', self.study.name, file.name)

    def import_all_entities(self):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_all_entities()

        """
        self.__log_import_start("all entities")
        for entity in self.import_order.keys():
            self.import_single_entity(entity)
