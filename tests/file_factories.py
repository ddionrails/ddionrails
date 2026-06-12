"""Factory to create temporary test files"""

import json
from abc import ABC
from csv import DictWriter
from dataclasses import dataclass
from os import mkdir, remove
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import mkdtemp
from typing import Any

from faker import Faker

from tests.model_factories import (
    AnalysisUnitFactory,
    AttachmentFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    DatasetFactory,
    InstrumentFactory,
    PeriodFactory,
    PublicationFactory,
    QuestionFactory,
    QuestionVariableFactory,
    StudyFactory,
    TopicFactory,
    TransformationFactory,
    VariableFactory,
)

FAKE = Faker()


@dataclass
class _PatchKwargs:
    target: str
    return_value: Path

    def keys(self):  # pylint: disable=missing-function-docstring
        return ["target", "return_value"]

    def __getitem__(self, item):
        return getattr(self, item)


def tmp_import_path(folder: Path | None = None) -> tuple[Path, _PatchKwargs]:
    """Take or create a tmp folder, return arguments to patch the global import path"""
    if folder is None:
        tmp_path = Path(mkdtemp())
    else:
        tmp_path = folder

    patch_dict = _PatchKwargs(
        target="ddionrails.studies.models.Study.import_path",
        return_value=tmp_path,
    )
    return tmp_path, patch_dict


def tmp_import_path_with_test_data() -> tuple[Path, _PatchKwargs]:
    """Move test data into patched import path"""
    csv_path = Path("./tests/functional/test_data/some-study/ddionrails/").absolute()
    tmp_path, patch_dict = tmp_import_path()
    copytree(csv_path, tmp_path, dirs_exist_ok=True)
    return tmp_path, patch_dict


def destroy_tmp_path(tmp_path: Path):
    """Use rmtree to remove directory."""
    tmp_path = Path(tmp_path)
    if tmp_path.exists():
        rmtree(tmp_path, ignore_errors=True)


class _TMPImportFILE(ABC):

    file_name: Path
    tmp_path: Path
    import_path_patch_arguments: _PatchKwargs
    folder_external: bool = False

    def __init__(self, folder: Path | None = None) -> None:
        if folder is not None:
            self.folder_external = True
        self.tmp_path, self.import_path_patch_arguments = tmp_import_path(folder)
        super().__init__()

    def __del__(self):
        if self.file_name.exists():
            remove(self.file_name)
        if not self.folder_external:
            rmtree(self.tmp_path)
        del self.tmp_path

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_name.exists():
            remove(self.file_name)
        if not self.folder_external:
            rmtree(self.tmp_path)
        del self.tmp_path

    @property
    def name(self) -> Path:
        """Path to the temp file created"""
        return self.file_name

    @property
    def parent_name(self) -> Path:
        """Path to the folder containing the created file"""
        return self.tmp_path

    @property
    def import_patch_arguments(self):
        """Arguments to be used in patch function for system data import path"""
        return self.import_path_patch_arguments


class TMPJSON(_TMPImportFILE):
    """Creates and fills temporary JSON file"""

    def __init__(
        self,
        content: dict[Any, Any] | list[Any],
        file_name: str = "",
        folder: Path | None = None,
    ):
        super().__init__(folder=folder)
        if file_name == "":
            file_name = FAKE.file_name(extension="json")
        self.file_name = self.tmp_path.joinpath(file_name)
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(content, file, ensure_ascii=False)


class TMPCSV(_TMPImportFILE):
    """Creates and fills temporary CSV file"""

    def __init__(
        self,
        content: list[dict[str, Any]],
        file_name: str = "",
        folder: Path | None = None,
    ):
        super().__init__(folder=folder)
        if file_name == "":
            file_name = FAKE.file_name(extension="csv")
        self.file_name = self.tmp_path.joinpath(file_name)
        with open(self.file_name, "w", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=content[0].keys())
            writer.writeheader()
            for row in content:
                writer.writerow(row)


# pylint: disable=too-many-locals,protected-access
def import_data_factory() -> (
    tuple[Path, _PatchKwargs, dict[str, _TMPImportFILE], dict[str, list[dict[str, str]]]]
):
    """Set up all files needed for a full import."""

    study = StudyFactory()
    dataset = DatasetFactory(study=study)
    concept = ConceptFactory(topics__size=3, topics__study=study, topics__depth=2)
    variables = [VariableFactory(dataset=dataset, concept=concept)]
    variables += [VariableFactory(dataset=dataset) for _ in range(3)]
    instrument = InstrumentFactory(study=study)
    questions = [
        QuestionFactory(
            instrument=instrument,
            question_items__cat_min=2,
            question_items__size=5,
            concepts_questions__size=2,
        )
    ]
    questions += [QuestionFactory(instrument=instrument) for _ in range(3)]
    publication = PublicationFactory(study=study)
    transformation = TransformationFactory(origin=variables[0], target=variables[1])
    question_variable = QuestionVariableFactory(
        question=questions[0], variable=variables[0]
    )
    attachment = AttachmentFactory(variable=variables[0])

    question_csv, answers_csv = ([], [])
    for question in questions:
        question_items, answers = QuestionFactory._to_csv(question)
        question_csv += question_items
        answers_csv += answers

    file_content = {
        "datasets.csv": [DatasetFactory._to_csv(dataset)],
        "concepts.csv": ConceptFactory._to_csv(concept),
        "topics.csv": TopicFactory._to_csv(concept.topics.first()),
        "analysis_units.csv": [
            AnalysisUnitFactory._to_csv(entity.analysis_unit)
            for entity in [dataset, instrument]
        ],
        "periods.csv": [
            PeriodFactory._to_csv(entity.analysis_unit)
            for entity in [dataset, instrument]
        ],
        "variables.csv": [VariableFactory._to_csv(variable) for variable in variables],
        "instruments.csv": [InstrumentFactory._to_csv(instrument)],
        "questions.csv": question_csv,
        "answers.csv": answers_csv,
        "publications.csv": [PublicationFactory._to_csv(publication)],
        "transformations.csv": [TransformationFactory._to_csv(transformation)],
        "questions_variables.csv": [QuestionVariableFactory._to_csv(question_variable)],
        "conceptual_datasets.csv": [
            ConceptualDatasetFactory._to_csv(dataset.conceptual_dataset)
        ],
        "attachments.csv": [AttachmentFactory._to_csv(attachment)],
    }

    tmp_path, patch_dict = tmp_import_path()

    files = {}
    for file_name, content in file_content.items():
        files[file_name] = TMPCSV(content=content, file_name=file_name, folder=tmp_path)

    mkdir(tmp_path.joinpath("datasets"))
    mkdir(tmp_path.joinpath("instruments"))
    instrument_file = f"{instrument.name}.json"
    dataset_file = f"{dataset.name}.json"

    file_content[instrument_file] = InstrumentFactory._to_json(instrument)
    files[instrument_file] = TMPJSON(
        content=file_content[instrument_file],
        file_name=instrument_file,
        folder=tmp_path.joinpath("instruments"),
    )
    file_content[dataset_file] = DatasetFactory._to_json(dataset)
    files[dataset_file] = TMPJSON(
        content=file_content[dataset_file],
        file_name=dataset_file,
        folder=tmp_path.joinpath("datasets"),
    )

    file_content["topics.json"] = TopicFactory._to_json(concept=concept)

    files["topics.json"] = TMPJSON(
        content=file_content["topics.json"],
        file_name="topics.json",
        folder=tmp_path,
    )

    return (tmp_path, patch_dict, files, file_content)
