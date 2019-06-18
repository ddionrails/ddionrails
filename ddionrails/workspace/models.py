# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app """

import csv
import io
import json
from typing import Dict, Union

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from config.helpers import render_markdown
from config.validators import validate_lowercase
from ddionrails.data.models import Variable
from ddionrails.studies.models import Study

from .scripts import ScriptConfig


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
        """ Returns a string representation using the "user.username" and "name" fields """
        return "%s/%s" % (self.user.username, self.name)

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "id" field """
        return reverse("workspace:basket", kwargs={"basket_id": self.id})

    def html_description(self) -> str:
        """ Returns the "description" field as a string containing HTML markup """
        return render_markdown(self.description)

    def title(self) -> str:
        """ Returns a title representation using the "label" field, with "name" field as fallback """
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


class BasketVariable(models.Model):
    """
    Stores a single basket variable,
    related to :model:`workspace.Basket` and :model:`data.Variable`
    """

    #############
    # relations #
    #############
    basket = models.ForeignKey(
        Basket,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to workspace.Basket",
    )
    variable = models.ForeignKey(
        Variable,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
    )

    class Meta:
        """ Django's metadata options """

        unique_together = ("basket", "variable")

    def clean(self):
        """ Custom clean method for BasketVariable
            the basket's study and the variable's dataset's study have to be the same.
        """
        basket_study = self.basket.study
        variable_study = self.variable.dataset.study
        if not basket_study == variable_study:
            raise ValidationError(
                f'Basket study "{basket_study}" does not match variable study "{variable_study}"'
            )
        super(BasketVariable, self).clean()


class Script(TimeStampedModel):
    """
    Stores a single script, related to :model:`workspace.Basket`.
    """

    ##############
    # attributes #
    ##############
    name = models.CharField(max_length=255, help_text="Name of the script")
    label = models.CharField(max_length=255, blank=True, help_text="Label of the script")
    generator_name = models.CharField(
        max_length=255,
        default="soep-stata",
        help_text="Name of the selected Script generator (e.g. soep-stata)",
    )
    settings = models.TextField(help_text="Settings of the script")

    #############
    # relations #
    #############
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, help_text="Foreign key to workspace.Basket"
    )

    def __str__(self) -> str:
        """ Returns a string representation using the "basket.id" and "id" fields """
        return f"/workspace/baskets/{self.basket.id}/scripts/{self.id}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "basket.id" and "id" fields """
        return reverse(
            "workspace:script_detail",
            kwargs={"basket_id": self.basket.id, "script_id": self.id},
        )

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

    def title(self) -> str:
        """ Returns a title representation using the "label" field, with "name" field as fallback """
        return str(self.label) if self.label != "" else str(self.name)
