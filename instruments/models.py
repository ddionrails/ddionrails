import copy
import json
import textwrap
from collections import OrderedDict

from django.db import models
from django.urls import reverse
from model_utils.managers import InheritanceManager

from concepts.models import AnalysisUnit, Concept, Period
from data.models import Variable
from ddionrails.mixins import ModelMixin as DorMixin
from ddionrails.validators import validate_lowercase
from elastic.mixins import ModelMixin as ElasticMixin
from studies.models import Study


class Instrument(ElasticMixin, DorMixin, models.Model):
    """
    Instrument.
    """

    name = models.CharField(
        max_length=255, validators=[validate_lowercase], db_index=True
    )
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    study = models.ForeignKey(
        Study, blank=True, null=True, related_name="instruments", on_delete=models.CASCADE
    )
    period = models.ForeignKey(
        Period,
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE,
    )
    analysis_unit = models.ForeignKey(
        AnalysisUnit,
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE,
    )

    objects = InheritanceManager()

    DOC_TYPE = "instrument"

    class Meta:
        unique_together = ("study", "name")
        ordering = ("study", "name")

    class DOR:
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "period", "analysis_unit"]

    def get_absolute_url(self):
        return reverse(
            "inst:instrument_detail",
            kwargs={"study_name": self.study.name, "instrument_name": self.name},
        )

    def layout_class(self):
        return "instrument"

    def __str__(self):
        return "%s/inst/%s" % (self.study, self.name)


class Question(ElasticMixin, DorMixin, models.Model):
    instrument = models.ForeignKey(
        Instrument,
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=255, validators=[validate_lowercase], db_index=True
    )
    label = models.CharField(max_length=255, blank=True)
    label_de = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sort_id = models.IntegerField(blank=True, null=True)
    image_url = models.TextField(blank=True)

    objects = InheritanceManager()

    DOC_TYPE = "question"

    class Meta:
        unique_together = ("instrument", "name")

    class DOR:
        id_fields = ["instrument", "name"]
        io_fields = ["name", "label", "description", "instrument"]

    def get_absolute_url(self):
        return reverse(
            "inst:question_detail",
            kwargs={
                "study_name": self.instrument.study.name,
                "instrument_name": self.instrument.name,
                "question_name": self.name,
            },
        )

    def layout_class(self):
        return "question"

    def get_answers(self):
        self.get_attribute["answers"]

    def previous_question(self):
        x = self.instrument.questions.get(sort_id=self.sort_id - 1)
        return x

    def next_question(self):
        x = self.instrument.questions.get(sort_id=self.sort_id + 1)
        return x

    def get_period(self, id=False, default=None):
        try:
            p = self.instrument.period
            if id == True:
                return p.id
            elif id == "name":
                return p.name
            else:
                return p
        except:
            return default

    def get_related_question_set(self, all_studies=False, by_study_and_period=False):
        concept_list = self.get_concepts()
        if all_studies:
            study_list = Study.objects.all()
        else:
            study_list = [self.instrument.study]
        direct_questions = Question.objects.filter(
            concepts_questions__concept_id__in=concept_list,
            instrument__study_id__in=study_list,
        )
        indirect_questions = Question.objects.filter(
            questions_variables__variable__concept__in=concept_list,
            instrument__study_id__in=study_list,
        )
        combined_set = direct_questions | indirect_questions
        combined_set = combined_set.distinct()
        if by_study_and_period:
            result = OrderedDict()
            for study in study_list:
                result[study.name] = OrderedDict()
                result[study.name]["no period"] = list()
                for period in study.periods.order_by("name"):
                    result[study.name][period.name] = list()
            for question in combined_set:
                result[question.instrument.study.name][
                    question.get_period(id="name", default="no period")
                ].append(question)
            return result
        else:
            return combined_set

    def get_concepts(self):
        direct_concepts = Concept.objects.filter(
            concepts_questions__question_id=self.pk
        )
        indirect_concepts = Concept.objects.filter(
            variables__questions_variables__question_id=self.pk
        )
        result = direct_concepts | indirect_concepts
        return result.distinct()

    def concept_list(self):
        """DEPRECATED NAME"""
        return self.get_concepts()

    def get_cs_name(self):
        x = self.get_source().get("question", "")
        if x != "":
            return x
        else:
            return self.name

    def title(self):
        if self.label != None and self.label != "":
            return self.label
        try:
            return self.items.first().title()
        except:
            return self.name

    def title_de(self):
        if self.label_de != None and self.label_de != "":
            return self.label
        try:
            return self.items.first().title_de()
        except:
            return self.name

    def __str__(self):
        return "%s/%s" % (self.instrument, self.name)

    def translation_languages(self):
        keys_first_item = copy.deepcopy(self.get_source()["items"])[0].keys()
        return [x.replace("text_", "") for x in keys_first_item if ("text_" in x)]

    def translate_item(self, item, language):
        item["text"] = item.get("text_%s" % language, item.get("text", ""))
        item["instruction"] = item.get(
            "instruction_%s" % language, item.get("instruction", "")
        )
        for answer in item.get("answers", []):
            answer["label"] = answer.get("label_%s" % language, answer.get("label", ""))

    def translations(self):
        results = {}
        try:
            for language in self.translation_languages():
                results[language] = self.item_array(language=language)
        except:
            pass
        return results

    def item_array(self, language=None):
        items = copy.deepcopy(self.get_source()["items"])
        items = items.values() if items.__class__ == dict else items
        for item in items:
            if language:
                self.translate_item(item, language)
            if "item" not in item:
                item["item"] = "root"
            if "sn" not in item:
                item["sn"] = 0
        items = sorted(items, key=lambda x: int(x["sn"]))
        before = None
        for i in range(len(items)):
            try:
                current = items[i]["answer_list"]
            except:
                current = None
            try:
                after = items[i + 1]["answer_list"]
            except:
                after = None
            if current and current == before:
                if current == after:
                    items[i]["layout"] = "matrix_element"
                else:
                    items[i]["layout"] = "matrix_footer"
            elif current and current == after:
                items[i]["layout"] = "matrix_header"
            else:
                items[i]["layout"] = "individual"
            before = current
        return items

    def to_topic_dict(self, language="en"):
        if language == "de":
            title = self.label_de if self.label_de != "" else self.title()
        else:
            title = self.title()
        try:
            concept_name = self.questions_variables.first().variable.concept.name
        except:
            concept_name = ""
        return dict(
            title=title,
            key="question_%s" % self.id,
            name=self.name,
            type="question",
            concept_key="concept_%s" % concept_name,
        )

    def comparison_string(self, to_string=False, wrap=50):
        cs = ["Question: %s" % self.title()]
        for item in self.get_source().get("items", []):
            cs += [
                "",
                "Item: %s (scale: %s)" % (item.get("item"), item.get("scale")),
                item.get("text", ""),
            ]
            cs += ["%s: %s" % (a["value"], a["label"]) for a in item.get("answers", [])]
        if wrap:
            cs_temp = [ textwrap.wrap(line, wrap) for line in cs ]
            cs = []
            for line_list in cs_temp:
                if line_list == []:
                    cs.append("")
                else:
                    cs += line_list
        if to_string:
            return "\n".join(cs)
        else:
            return cs


class QuestionVariable(models.Model):
    """
    Linking items in an instrument with related variables.
    """

    question = models.ForeignKey(
        Question, related_name="questions_variables", on_delete=models.CASCADE
    )
    variable = models.ForeignKey(
        Variable, related_name="questions_variables", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("question", "variable")

    class DOR:
        id_fields = ["question", "variable"]
        io_fields = ["question", "variable"]


class ConceptQuestion(models.Model):
    """
    Linking items in an instrument with related variables.
    """

    question = models.ForeignKey(
        Question, related_name="concepts_questions", on_delete=models.CASCADE
    )
    concept = models.ForeignKey(
        Concept, related_name="concepts_questions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("question", "concept")
