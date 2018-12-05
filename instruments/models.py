import copy

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

    name = models.CharField(max_length=255, validators=[validate_lowercase], db_index=True)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    study = models.ForeignKey(Study, blank=True, null=True, related_name="instruments", on_delete=models.CASCADE)
    period = models.ForeignKey(Period, blank=True, null=True, related_name="instruments", on_delete=models.CASCADE)
    analysis_unit = models.ForeignKey(
        AnalysisUnit, blank=True, null=True, related_name="instruments", on_delete=models.CASCADE
    )

    objects = InheritanceManager()

    DOC_TYPE = "instrument"

    class Meta:
        unique_together = ("study", "name")

    class DOR:
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "period", "analysis_unit"]

    def get_absolute_url(self):
        return reverse("inst:instrument_detail", kwargs={"study_name": self.study.name, "instrument_name": self.name})

    def layout_class(self):
        return "instrument"

    def __str__(self):
        return "%s/inst/%s" % (self.study, self.name)


class Question(ElasticMixin, DorMixin, models.Model):
    instrument = models.ForeignKey(
        Instrument, blank=True, null=True, related_name="questions", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, validators=[validate_lowercase], db_index=True)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sort_id = models.IntegerField(blank=True, null=True)

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

    def concept_list(self):
        return Concept.objects.filter(concepts_questions__question_id=self.pk).all()

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

    def __str__(self):
        return "%s/%s" % (self.instrument, self.name)

    def translation_languages(self):
        keys_first_item = copy.deepcopy(self.get_source()["items"])[0].keys()
        return [x.replace("text_", "") for x in keys_first_item if ("text_" in x)]

    def translate_item(self, item, language):
        item["text"] = item.get("text_%s" % language, item.get("text", ""))
        item["instruction"] = item.get("instruction_%s" % language, item.get("instruction", ""))
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


class QuestionVariable(models.Model):
    """
    Linking items in an instrument with related variables.
    """

    question = models.ForeignKey(Question, related_name="questions_variables", on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, related_name="questions_variables", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "variable")

    class DOR:
        id_fields = ["question", "variable"]
        io_fields = ["question", "variable"]


class ConceptQuestion(models.Model):
    """
    Linking items in an instrument with related variables.
    """

    question = models.ForeignKey(Question, related_name="concepts_questions", on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, related_name="concepts_questions", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "concept")
