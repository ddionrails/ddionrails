import logging
from collections import OrderedDict

from concepts.models import Period
from data.models import Dataset, Variable
from imports import imports
from instruments.models import Instrument, Question

from .forms import AttachmentForm, PublicationForm
from .models import Publication

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class PublicationImport(imports.CSVImport):
    class DOR:
        form = PublicationForm

    def process_element(self, element: OrderedDict) -> OrderedDict:
        element["study"] = self.study.id
        return element

    def import_element(self, element: OrderedDict) -> Publication:
        import_object = super().import_element(element)
        try:
            import_object.set_elastic(import_object.to_elastic_dict())
        except:
            logger.error(f'Failed to import publication "{element["name"]}"')
        return import_object


class AttachmentImport(imports.CSVImport):
    class DOR:
        form = AttachmentForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.study.related_attachments.all().delete()

    def process_element(self, element):
        element["context_study"] = self.study.id
        t = element.get("type")
        if t == "study":
            element["study"] = self.study.id
        elif t == "variable":
            element["variable"] = (
                Variable.objects.filter(
                    dataset__study_id=self.study.id,
                    dataset__name=element.get("dataset_name"),
                )
                .get(name=element.get("variable_name"))
                .id
            )
        elif t == "dataset":
            element["dataset"] = (
                Dataset.objects.filter(study_id=self.study.id)
                .get(name=element.get("dataset_name"))
                .id
            )
        elif t == "question":
            element["question"] = (
                Question.objects.filter(
                    instrument__study_id=self.study.id,
                    instrument__name=element.get("instrument_name"),
                )
                .get(name=element.get("question_name"))
                .id
            )
        elif t == "instrument":
            element["instrument"] = (
                Instrument.objects.filter(study_id=self.study.id)
                .get(name=element.get("instrument_name"))
                .id
            )
        return element
