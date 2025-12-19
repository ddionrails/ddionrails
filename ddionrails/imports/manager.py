# -*- coding: utf-8 -*-

"""Manager classes for imports in ddionrails project"""

import csv
import json
import logging
import sys
from collections import OrderedDict
from inspect import isfunction
from os import remove
from pathlib import Path
from types import FunctionType
from typing import Any, Tuple
from urllib.request import urlopen, urlretrieve

import django_rq
from django.conf import settings

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
    siblings_generation,
    TransformationImport,
    VariableImport,
    variables_images_import,
)
from ddionrails.imports.git_repos import clean_repo_url
from ddionrails.instruments.imports import (
    concept_question_import,
    instrument_import,
    question_image_import,
    question_import,
    question_variable_import,
)
from ddionrails.publications.imports import AttachmentImport, PublicationImport
from ddionrails.studies.imports import StudyDescriptionImport
from ddionrails.studies.models import Study
from ddionrails.workspace.imports import script_metadata_import

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


def _initialize_studies():
    study_init_file: str = settings.STUDY_INIT_FILE

    data = []

    if study_init_file.startswith("http"):
        with urlopen(study_init_file) as webcontent:  # nosec
            data = json.loads(webcontent.read())
    else:
        file_path = Path(study_init_file)
        if file_path.exists() and file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
    for study in data:
        if "name" not in study or "repo" not in study:
            continue
        study_object, _ = Study.objects.get_or_create(name=study["name"])
        if not study_object.label:
            study_object.label = study.get("label", study["name"])
        study_object.pin_reference = study.get("ref", study_object.pin_reference)

        study_object.repo = clean_repo_url(study["repo"])
        study_object.save()


def _import_home_background():

    static_path = Path("./static")
    if getattr(settings, "STATIC_ROOT", ""):
        static_path = Path(settings.STATIC_ROOT)
    elif getattr(settings, "STATICFILES_DIRS", ""):
        static_path = settings.BASE_DIR.joinpath("static")

    image_path = static_path.joinpath("background.png")
    if image_path.exists():
        remove(image_path)

    # Copy background image to static/
    if str(settings.HOME_BACKGROUND_IMAGE).startswith("http"):
        urlretrieve(settings.HOME_BACKGROUND_IMAGE, image_path)  # nosec


def system_import():
    """Import the files from the system repository."""

    _initialize_studies()
    _import_home_background()


class StudyImportManager:
    """Manage the import of all study resources."""

    import_order: OrderedDict[str, Tuple[Any, Any]]

    def __init__(self, study: Study, redis: bool = True):
        self.study = study
        self.base_dir = study.import_path()
        self._concepts_fixed = False
        self.redis = redis

        self.import_order = OrderedDict(
            {
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
                "study": (StudyDescriptionImport, self.base_dir / "study.md"),
                "siblings": (siblings_generation, self.base_dir / "study.md"),
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
