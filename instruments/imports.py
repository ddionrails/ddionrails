import json
import logging
from collections import OrderedDict

from concepts.models import Concept, Period
from data.models import Variable
from ddionrails.helpers import lower_dict_names
from imports import imports

from .models import ConceptQuestion, Instrument, Question, QuestionVariable

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class InstrumentImport(imports.Import):
    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_instrument(self.name, self.content)

    def _import_instrument(self, name, content):
        import_dict = dict(study=self.study, name=name)
        instrument = Instrument.get_or_create(import_dict)

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
        period, status = Period.objects.get_or_create(name=period_name, study=self.study)
        instrument.period = period

        for name, q in content["questions"].items():
            import_dict = dict(name=q["question"], instrument=instrument)
            question = Question.get_or_create(import_dict)
            question.sort_id = int(q.get("sn", 0))
            question.label = q.get("label", q.get("text", name))
            question.label_de = q.get("label_de", q.get("text_de", ""))
            question.image_url = q.get("image_url", "")
            question.save()
            q["namespace"] = self.study.name
            q["instrument"] = instrument.name
            question.set_elastic(q)
        instrument.label = content.get("label", "")
        instrument.description = content.get("description", "")
        instrument.save()


class QuestionVariableImport(imports.CSVImport):
    def execute_import(self):
        for link in self.content:
            self._import_link(link)

    def _import_link(self, link):
        try:
            lower_dict_names(link)
            question = self._get_question(link)
            variable = self._get_variable(link)
            qv_link = QuestionVariable.objects.get_or_create(
                question=question, variable=variable
            )
        except:
            variable = (
                f"{link['study_name']}/{link['dataset_name']}/{link['variable_name']}"
            )
            question = (
                f"{link['study_name']}/{link['instrument_name']}/{link['question_name']}"
            )
            logger.error(f'Could not link variable "{variable}" to question "{question}"')

    def _get_question(self, link):
        question = (
            Question.objects.filter(instrument__study__name=link["study_name"])
            .filter(instrument__name=link["instrument_name"])
            .get(name=link["question_name"])
        )
        return question

    def _get_variable(self, link):
        variable = (
            Variable.objects.filter(dataset__study__name=link["study_name"])
            .filter(dataset__name=link["dataset_name"])
            .filter(name=link["variable_name"])
            .first()
        )
        return variable


class ConceptQuestionImport(imports.CSVImport):
    def execute_import(self):
        for link in self.content:
            self._import_link(link)

    def _import_link(self, link):
        try:
            lower_dict_names(link)
            question = self._get_question(link)
            concept = self._get_concept(link)
            qv_link = ConceptQuestion.objects.get_or_create(
                question=question, concept=concept
            )
        except:
            question = (
                f"{link['study_name']}/{link['instrument_name']}/{link['question_name']}"
            )
            concept = link["concept_name"]
            logger.error(f'Could not link concept "{concept}" to question "{question}"')

    def _get_question(self, link):
        question = (
            Question.objects.filter(instrument__study__name=link["study_name"])
            .filter(instrument__name=link["instrument_name"])
            .get(name=link["question_name"])
        )
        return question

    def _get_concept(self, link):
        concept, status = Concept.objects.get_or_create(name=link["concept_name"])
        return concept
