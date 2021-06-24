# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.publications app """

import json
import logging
from collections import OrderedDict
from typing import Dict

from django.db.models import Model
from django.db.transaction import atomic

from ddionrails.data.models import Dataset, Variable
from ddionrails.imports import imports
from ddionrails.instruments.models import Instrument, Question
from ddionrails.publications.models import Attachment

from .forms import AttachmentForm, PublicationForm

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class PublicationImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = PublicationForm

    def process_element(self, element: OrderedDict) -> OrderedDict:
        element["study"] = self.study.id
        return element


class AttachmentImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = AttachmentForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.study.related_attachments.all().delete()

    @atomic
    def execute_import(self):
        for attachment in self.content:
            try:
                attachment = self._process_field_names(attachment)
                related = self._get_related_object(attachment)
                attachment = dict(
                    **related, url=attachment["url"], url_text=attachment["url_text"]
                )
                self.import_element(attachment)
            except BaseException as error:
                raise type(error)(
                    "\n"
                    + json.dumps(
                        attachment,
                        default=str,
                        ensure_ascii=False,
                        sort_keys=True,
                        indent=4,
                        separators=(",", ": "),
                    )
                )

    def import_element(self, element):
        attachment = Attachment()
        attachment.context_study = self.study
        for key, value in element.items():
            setattr(attachment, key, value)
        attachment.save()

    @staticmethod
    def _process_field_names(dictionairy: Dict[str, str]) -> Dict[str, str]:
        """Replace outdated field names

        Remove the outdated "_name" prefix from  dictionairy keys.

        Returns:
            New dictionairy with "_name" removed from keys.
        """
        cleaned_dictionairy = dict()
        for key, value in dictionairy.items():
            if key[-5:] == "_name":
                cleaned_dictionairy[key[:-5]] = value
            else:
                cleaned_dictionairy[key] = value
        return cleaned_dictionairy

    def _get_related_object(self, element: Dict[str, str]) -> Dict[str, Model]:
        """Retrieve the attachement target from the database.

        Arguments:
            element: Metadata about the target object of the attachment.

        Returns:
            A single key dictionairy where the key is the field name of the
            target and the value is the target object.
        """
        element["context_study"] = self.study
        _type = element.get("type")
        dataset = element.get("dataset")
        if _type == "study":
            return {"study": self.study}
        call_dict = {
            "variable": (
                Variable,
                {
                    "dataset__study": self.study,
                    "dataset__name": dataset,
                    "name": element.get("variable"),
                },
            ),
            "dataset": (Dataset, {"name": element.get("dataset"), "study": self.study}),
            "question": (
                Question,
                {
                    "instrument__study": self.study,
                    "instrument__name": element.get("instrument"),
                    "name": element.get("question"),
                },
            ),
            "instrument": (
                Instrument,
                {"study": self.study, "name": element.get("instrument")},
            ),
        }
        model, kwargs = call_dict[_type]
        _object = model.objects.get(**kwargs)
        return {_type: _object}
