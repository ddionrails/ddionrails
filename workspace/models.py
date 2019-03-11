import csv
import io
import json

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from data.models import Variable
from ddionrails.helpers import render_markdown
from ddionrails.validators import validate_lowercase
from elastic.mixins import ModelMixin as ElasticMixin
from studies.models import Study

from .scripts import ScriptConfig


class Basket(ElasticMixin, TimeStampedModel):
    """
    Basket
    """

    name = models.CharField(max_length=255, validators=[validate_lowercase])
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    security_token = models.CharField(max_length=255, blank=True)
    study = models.ForeignKey(Study, related_name="baskets", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="baskets", on_delete=models.CASCADE)
    variables = models.ManyToManyField(Variable, through="BasketVariable")
    # TODO Validate that the variable is part of the study.

    DOC_TYPE = "basket"

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return "%s/%s" % (self.user.username, self.name)

    def get_absolute_url(self):
        return reverse("workspace:basket", kwargs={"basket_id": self.id})

    def html_description(self):
        return render_markdown(self.description)

    def title(self):
        return self.label if self.label != "" else self.name

    @classmethod
    def get_or_create(cls, name, user):
        name = name.lower()
        if user.__class__ == str:
            user = User.objects.get(username=user)
        basket, created = cls.objects.get_or_create(name=name, user=user)
        return basket

    def get_script_generators(self):
        try:
            config = self.study.get_config()
            return config["script_generators"]
        except (TypeError, KeyError):
            return None

    def to_csv(self):
        fieldnames = [
            "name",
            "label",
            "label_de",
            "dataset_name",
            "dataset_label",
            "dataset_label_de",
            "study_name",
            "study_label",
            "study_label_de",
            "concept_name",
            "period_name",
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for variable in self.variables.all():
            row = dict(
                name=variable.name,
                label=variable.label,
                label_de=variable.label_de,
                dataset_name=variable.dataset.name,
                dataset_label=variable.dataset.label,
                dataset_label_de=variable.dataset.label_de,
                study_name=variable.dataset.study.name,
                study_label=variable.dataset.study.label,
                study_label_de=variable.dataset.study.label_de,
            )
            try:
                row["concept_name"] = variable.concept.name
            except AttributeError:
                pass
            try:
                row["period_name"] = variable.dataset.period.name
            except AttributeError:
                pass
            writer.writerow(row)
        return output.getvalue()

    def to_dict(self):
        return dict(name=self.name, label=self.label, id=self.id)


class BasketVariable(models.Model):
    basket = models.ForeignKey(
        Basket, related_name="baskets_variables", on_delete=models.CASCADE
    )
    variable = models.ForeignKey(
        Variable, related_name="baskets_variables", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("basket", "variable")


class Script(TimeStampedModel):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    generator_name = models.CharField(max_length=255, default="soep-stata")
    label = models.CharField(max_length=255, blank=True)
    settings = models.TextField()

    def get_config(self):
        config_name = self.generator_name
        if not hasattr(self, "local_config"):
            self.local_config = ScriptConfig.get_config(config_name)(self, self.basket)
            settings = self.local_config.DEFAULT_DICT.copy()
            settings.update(self.get_settings())
            if sorted(settings.keys()) != sorted(self.get_settings().keys()):
                self.settings_dict = settings
                self.settings = json.dumps(settings)
                self.save()
        return self.local_config

    def get_settings(self):
        if not hasattr(self, "settings_dict"):
            self.settings_dict = json.loads(self.settings)
        return self.settings_dict

    def get_script_input(self):
        return self.get_config().get_script_input()

    def title(self):
        return self.label if self.label != "" else self.name

    def __str__(self):
        return "/workspace/baskets/%s/scripts/%s" % (self.basket.id, self.id)

    def get_absolute_url(self):
        return reverse(
            "workspace:script_detail",
            kwargs={"basket_id": self.basket.id, "script_id": self.id},
        )
