# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app: Script """

import json

from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from ddionrails.workspace.scripts import ScriptConfig

from .basket import Basket


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
