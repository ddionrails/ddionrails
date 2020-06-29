# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app: Basket """

import csv
import io
from pathlib import Path
from typing import Dict, Union

from django.apps import apps
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from config.helpers import render_markdown
from config.validators import validate_lowercase
from ddionrails.data.models import Variable
from ddionrails.studies.models import Study


class Basket(TimeStampedModel):
    """
    Stores a single basket,
    related to :model:`studies.Study`, :model:`auth.User` and :model:`data.Variable`.
    """

    ##############
    # attributes #
    ##############
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        help_text="Name of the basket (Lowercase)",
    )
    label = models.CharField(
        max_length=255, blank=True, verbose_name="Label", help_text="Label of the basket"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown)",
        help_text="Description of the basket (Markdown)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="baskets",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
        db_constraint=False,
    )
    user = models.ForeignKey(
        User,
        related_name="baskets",
        on_delete=models.CASCADE,
        help_text="Foreign key to auth.User",
    )
    variables = models.ManyToManyField(
        Variable,
        through="BasketVariable",
        help_text="ManyToMany relation to data.Variable",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("user", "name")

    def __str__(self) -> str:
        """ Create a pathlike string to reach this basket from the frontend."""
        return "%s/%s" % (self.user.username, self.name)

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "id" field """
        return reverse("workspace:basket_detail", kwargs={"basket_id": self.id})

    def html_description(self) -> str:
        """ Returns the "description" field as a string containing HTML markup """
        return render_markdown(self.description)

    def title(self) -> str:
        """ Returns a title representation.

        Uses the "label" field, with "name" field as fallback
        """
        return str(self.label) if self.label != "" else str(self.name)

    @classmethod
    def get_or_create(cls, name, user):
        name = name.lower()
        if user.__class__ == str:
            user = User.objects.get(username=user)
        basket = cls.objects.get_or_create(name=name, user=user)[0]
        return basket

    def get_script_generators(self):
        try:
            return self.study.config["script_generators"]
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

    def to_dict(self) -> Dict[str, Union[int, str]]:
        """ Returns a dictionary containing the fields: name, label and id """
        return dict(name=self.name, label=self.label, id=self.id)

    @staticmethod
    def backup():
        """Create a backup file for baskets and their content."""
        basket_variables = apps.get_model("workspace", "BasketVariable")
        objects = list(Basket.objects.all()) + list(basket_variables.objects.all())
        json_serializer = serializers.get_serializer("json")
        serializer = json_serializer()
        filename = Path("file.json").absolute()

        with open(filename, "w") as out:
            serializer.serialize(objects, stream=out)
        return filename
