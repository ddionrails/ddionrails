# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import json
import logging
from collections import OrderedDict

from ddionrails.concepts.models import AnalysisUnit, Period
from ddionrails.imports import imports
from ddionrails.instruments.models import Instrument, Question

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


class InstrumentImport(imports.Import):
    """Import a single Instrument and its containing questions.

    Is called with a single instrument JSON file.
    Also imports associated Periods and analysis_units, if they are not
    already present.
    """

    content: str

    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_instrument(self.name, self.content)

    def _import_instrument(self, name, content):
        instrument, _ = Instrument.objects.get_or_create(study=self.study, name=name)

        # add period relation to instrument
        period_name = content.get("period", "none")
        # Workaround for two ways to name period: period, period_name
        # => period_name
        if period_name == "none":
            period_name = content.get("period_name", "none")

        # Workaround for periods coming in as float, w.g. 2001.0
        try:
            period_name = str(int(period_name))
        except ValueError:
            period_name = str(period_name)
        period = Period.objects.get_or_create(name=period_name, study=self.study)[0]
        instrument.period = period

        # add analysis_unit relation to instrument
        analysis_unit_name = content.get("analysis_unit", "none")
        if analysis_unit_name == "none":
            analysis_unit_name = content.get("analysis_unit_name", "none")
        analysis_unit = AnalysisUnit.objects.get_or_create(
            name=analysis_unit_name, study=self.study
        )[0]
        instrument.analysis_unit = analysis_unit

        for _name, _question in content["questions"].items():
            question, _ = Question.objects.get_or_create(
                name=_question["question"], instrument=instrument
            )
            question.sort_id = int(_question.get("sn", 0))
            question.label = _question.get("label", _question.get("text", _name))
            question.label_de = _question.get("label_de", _question.get("text_de", ""))
            question.description = _question.get("description", "")
            question.description_de = _question.get("description_de", "")
            question.items = _question.get("items", list)
            question.save()

        instrument.label = content.get("label", "")
        instrument.label_de = content.get("label_de", "")
        instrument.description = content.get("description", "")
        instrument.description_de = content.get("description_de", "")
        instrument.save()
