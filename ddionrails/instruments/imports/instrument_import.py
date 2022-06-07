# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import json
from collections import OrderedDict
from csv import DictReader
from pathlib import Path
from typing import Dict, Set

from ddionrails.concepts.models import AnalysisUnit, Period
from ddionrails.imports import imports
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models import Instrument, Question
from ddionrails.studies.models import Study

required_fields = [
    "name",
    "label",
    "label_de",
    "description",
    "description_de",
]

optional_fields = ["mode"]
optional_nested_fields: Dict[str, Dict[str, str]] = {
    "type": {"position": "type_position", "en": "type", "de": "type_de"}
}


def _get_instruments_with_questions(base_path: Path) -> Set[str]:
    instruments_with_questions = set()
    with open(base_path / "questions.csv", encoding="utf8") as questions_csv:
        for row in DictReader(questions_csv):
            instruments_with_questions.add(row["instrument"])
    return instruments_with_questions


def instrument_import(file: Path, study: Study) -> None:
    """Import instrument data from CSV"""
    instruments_with_questions = _get_instruments_with_questions(file.parent)

    periods = {period.name: period for period in Period.objects.filter(study=study)}
    analysis_units = {
        unit.name: unit for unit in AnalysisUnit.objects.filter(study=study)
    }

    with open(file, encoding="utf8") as instruments_csv:
        instruments = []
        for row in DictReader(instruments_csv):
            instrument = Instrument()
            instrument.study = study
            instrument.id = hash_with_namespace_uuid(  # pylint: disable=invalid-name
                study.id, row["name"], cache=False
            )
            instrument.period = periods.get(row["period"], None)
            instrument.analysis_unit = analysis_units.get(row["analysis_unit"], None)

            for field in required_fields:
                setattr(instrument, field, row[field])
            for field in optional_fields:
                setattr(instrument, field, row.get(field, ""))
            for field, field_mapper in optional_nested_fields.items():
                value = {}
                for model_field, csv_field in field_mapper.items():
                    value[model_field] = row[csv_field]
                setattr(instrument, field, value)
            instrument.has_questions = instrument.name in instruments_with_questions

            instruments.append(instrument)

    Instrument.objects.bulk_update(
        instruments,
        required_fields
        + ["analysis_unit", "period", "has_questions"]
        + optional_fields
        + list(optional_nested_fields.keys()),
    )


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
