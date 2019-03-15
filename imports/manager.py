import glob
import logging
import os
import re
from collections import OrderedDict
from pathlib import Path

import django_rq
from django.conf import settings

from concepts.imports import (
    AnalysisUnitImport,
    ConceptImport,
    ConceptualDatasetImport,
    PeriodImport,
    TopicImport,
    TopicJsonImport,
)
from data.imports import (
    DatasetImport,
    DatasetJsonImport,
    TransformationImport,
    VariableImport,
)
from ddionrails.helpers import script_list, script_list_output
from instruments.imports import (
    ConceptQuestionImport,
    InstrumentImport,
    QuestionVariableImport,
)
from publications.imports import AttachmentImport, PublicationImport
from studies.imports import StudyDescriptionImport, StudyImport
from studies.models import Study

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, study_or_system):
        self.study_or_system = study_or_system
        self.link = study_or_system.repo_url()
        self.name = study_or_system.name
        self.path = os.path.join(settings.IMPORT_REPO_PATH, self.name)

    def clone_repo(self):
        script = [
            f"cd {settings.IMPORT_REPO_PATH}",
            f"git clone --depth 1 {self.link} {self.name} -b {settings.IMPORT_BRANCH}",
            f"cd {self.name}",
            f"git checkout -b {settings.IMPORT_BRANCH} origin/{settings.IMPORT_BRANCH}",
            f"git branch --set-upstream-to=origin/{settings.IMPORT_BRANCH} {settings.IMPORT_BRANCH}",
        ]
        script_list(script)

    def set_branch(self, branch=settings.IMPORT_BRANCH):
        script = ["cd %s" % self.path, "git checkout %s" % branch]
        script_list(script)

    def update_repo(self):
        script = ["cd %s" % self.path, "git pull"]
        script_list(script)

    def update_or_clone_repo(self):
        print("[INFO] Repository path: %s" % self.path)
        if os.path.isdir(self.path):
            self.update_repo()
        else:
            self.clone_repo()

    def get_commit_id(self):
        script = ["cd %s" % self.path, "git log --pretty=format:'%H' -n 1"]
        return script_list_output(script)

    def set_commit_id(self):
        study_or_system = self.study_or_system
        study_or_system.current_commit = self.get_commit_id()
        study_or_system.save()

    def import_required(self):
        return self.study_or_system.current_commit != self.get_commit_id()

    def list_changed_files(self):
        script = [
            "cd %s" % self.path,
            "git diff --name-only %s -- %s"
            % (self.study_or_system.current_commit, settings.IMPORT_SUB_DIRECTORY),
        ]
        return script_list_output(script).split()

    def list_all_files(self):
        script = ["cd %s" % self.path, "find %s" % settings.IMPORT_SUB_DIRECTORY]
        return script_list_output(script).split()

    def import_list(self, import_all=False):
        if import_all:
            import_files = self.list_all_files()
        else:
            import_files = self.list_changed_files()
        return import_files


class ImportLink:
    def __init__(self, expression, importer, activate_import=True):

        print(expression)
        print(importer)
        print(activate_import)

        self.expression = re.compile(expression)
        self.importer = importer
        self.activate_import = activate_import

    def run_import(self, import_files, study=None):
        if self.activate_import:
            for import_file in import_files:
                self._process_import_file(import_file, study=study)

    def _import(self, study, import_file):
        self.importer.run_import(import_file, study=study)

    def _process_import_file(self, import_file, study=None):
        # import_file = import_file.replace(settings.IMPORT_SUB_DIRECTORY, "")
        if self._match(import_file):
            django_rq.enqueue(self._import, study, import_file)

    def _match(self, import_file):
        return True if self.expression.match(import_file) else False


class SystemImportManager:
    """Import the files from the system repository."""

    def __init__(self, system):
        self.system = system
        self.repo = Repository(system)
        self.import_patterns = [ImportLink("^studies.csv$", StudyImport)]

    def run_import(self, import_all=False):
        """
        Run the system import.
        """
        if import_all or self.system.repo_url() == "":
            import_files = self.repo.list_all_files()
        else:
            import_files = self.repo.list_changed_files()
        for link in self.import_patterns:
            link.run_import(import_files, self.system)
        self.repo.set_commit_id()


# class StudyImportManager:
#     """
#     The ``StudyImportManager`` controls the automated imports for a study.
#     """
#
#     def __init__(self, study):
#         self.study = study
#         self.repo = Repository(study)
#         self.import_patterns = [
#             ImportLink("^study.md$", StudyDescriptionImport),
#             ImportLink("^topics.csv$", TopicImport),
#             ImportLink("^topics.json$", TopicJsonImport),
#             ImportLink("^concepts.csv$", ConceptImport),
#             ImportLink("^analysis_units.csv$", AnalysisUnitImport),
#             ImportLink("^periods.csv$", PeriodImport),
#             ImportLink("^conceptual_datasets.csv$", ConceptualDatasetImport),
#             ImportLink(r"^instruments\/.*\.json$", InstrumentImport),
#             ImportLink(r"^datasets\/.*\.json$", DatasetJsonImport),
#             ImportLink("^datasets.csv$", DatasetImport),
#             ImportLink("^variables.csv$", VariableImport),
#             ImportLink("^questions_variables.csv$", QuestionVariableImport),
#             ImportLink("^concepts_questions.csv$", ConceptQuestionImport),
#             ImportLink("^transformations.csv$", TransformationImport),
#             ImportLink("^attachments.csv$", AttachmentImport),
#             ImportLink("^publications.csv$", PublicationImport),
#         ]
#
#     def run_import(self, import_all=False):
#         """
#         Run the study import. Parameters:
#
#         import all
#             If set to ``True``, all files in the repo will be imported.
#         """
#         if import_all or self.study.repo_url() == "":
#             import_files = self.repo.list_all_files()
#         else:
#             import_files = self.repo.list_changed_files()
#         for link in self.import_patterns:
#             link.run_import(import_files, self.study)
#         self.repo.set_commit_id()
#         # django_rq.enqueue(Concept.index_all) # moved to scripts/import.py


class StudyImportManager:
    def __init__(self, study: Study):
        self.study = study
        self.repo = Repository(study)
        self.base_dir = Path(
            f"{settings.IMPORT_REPO_PATH}/{self.study}/{settings.IMPORT_SUB_DIRECTORY}/"
        )

        self.IMPORT_ORDER = OrderedDict(
            {
                "study": (StudyDescriptionImport, self.base_dir / "study.md"),
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
            }
        )

    def update_repo(self):
        self.repo.update_repo()
        self.repo.set_commit_id()

    def import_single_entity(self, entity: str, filename: bool = None):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_single_entity("study")
        manager.import_single_entity("periods")
        manager.import_single_entity("instruments", "instruments/some-instrument.json")

        """
        logger.info(f'Study "{self.study.name}" starts import of entity: "{entity}"')
        importer_class, default_file_path = self.IMPORT_ORDER.get(entity)

        # import specific file
        if filename:
            file = self.base_dir / filename
            if file.is_file():
                logger.info(
                    f'Study "{self.study.name}" starts import of file: "{file.name}"'
                )
                importer = importer_class(file, self.study)
                django_rq.enqueue(importer.run_import, file, self.study)
            else:
                logger.error(f'Study "{self.study.name}" has no file: "{file.name}"')
        else:

            # single file import
            if isinstance(default_file_path, Path):
                if default_file_path.is_file():
                    importer = importer_class(default_file_path, self.study)
                    django_rq.enqueue(importer.run_import, default_file_path, self.study)
                else:
                    logger.warning(
                        f'Study "{self.study.name}" has no file: "{default_file_path.name}"'
                    )

            # multiple files import, e.g. instruments, datasets
            else:

                for file in sorted(default_file_path):
                    logger.info(
                        f'Study "{self.study.name}" starts import of file: "{file.name}"'
                    )
                    importer = importer_class(file, self.study)
                    django_rq.enqueue(importer.run_import, file, self.study)

    def import_all_entities(self):
        """
        Example usage:

        study = Study.objects.get(name="some-study")
        manager = StudyImportManager(study)

        manager.import_all_entities()

        """
        logger.info(f'Study "{self.study.name}" starts importing of all entities')
        for entity in self.IMPORT_ORDER.keys():
            self.import_single_entity(entity)


# class LocalImport:
#     def __init__(self, study_name=""):
#         if study_name != "":
#             self.study = Study.objects.get(name=study_name)
#         else:
#             self.study = Study.objects.first()
#         self.repo = Repository(self.study)
#
#     def update_repo(self):
#         self.repo.update_repo()
#
#     def run_import(self, filename):
#         importer_dict = {
#             "study.md": StudyDescriptionImport,
#             "topics.csv": TopicImport,
#             "topics.json": TopicJsonImport,
#             "concepts.csv": ConceptImport,
#             "analysis_units.csv": AnalysisUnitImport,
#             "periods.csv": PeriodImport,
#             "conceptual_datasets.csv": ConceptualDatasetImport,
#             "datasets.csv": DatasetImport,
#             "variables.csv": VariableImport,
#             "transformations.csv": TransformationImport,
#             "questions_variables.csv": QuestionVariableImport,
#             "concepts_questions.csv": ConceptQuestionImport,
#             "attachments.csv": AttachmentImport,
#             "publications.csv": PublicationImport,
#         }
#         self._enqueue_import(filename, importer_dict[filename])
#
#     def import_datasets(self, filename=None):
#         if filename:
#             self._enqueue_import(filename, DatasetJsonImport)
#         else:
#             files = self._get_json_files("datasets")
#             for filename in files:
#                 self._enqueue_import(filename, DatasetJsonImport)
#
#     def import_instruments(self, filename=None):
#         if filename:
#             self._enqueue_import(filename, InstrumentImport)
#         else:
#             files = self._get_json_files("instruments")
#             for filename in files:
#                 self._enqueue_import(filename, InstrumentImport)
#
#     def _get_json_files(self, dir_name):
#         filelist = glob.glob(
#             os.path.join(self.repo.path, settings.IMPORT_SUB_DIRECTORY, dir_name, "*json")
#         )
#         filelist = [
#             x.replace(os.path.join(self.repo.path, settings.IMPORT_SUB_DIRECTORY), "")
#             for x in filelist
#         ]
#         return filelist
#
#     def _import(self, import_file, importer):
#         importer.run_import(import_file, study=self.study)
#
#     def _enqueue_import(self, import_file, importer):
#         import_file = import_file.replace(settings.IMPORT_SUB_DIRECTORY, "")
#         django_rq.enqueue(self._import, import_file, importer)
