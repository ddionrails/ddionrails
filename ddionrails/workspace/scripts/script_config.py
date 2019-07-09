# -*- coding: utf-8 -*-

""" Script generators for ddionrails.workspace app: ScriptConfig """

import json
from collections import defaultdict


class ScriptConfig:
    """
    The sub-class has to initialize at least three inputs:

    -   template (string)
    -   fields (list)
    -   default_settings (dict)
    """

    NAME = "abstract-script"

    def __init__(self, script, basket):
        self.basket = basket
        self.script = script

    def get_script_input(self):
        return dict(
            settings=json.loads(self.script.settings),
            data=self.get_datasets_and_variables(),
            template=self.template,
        )

    def get_datasets_and_variables(self):
        datasets = defaultdict(list)
        for variable in self.basket.variables.all():
            dataset_name = variable.dataset.name
            variable_name = variable.name
            datasets[dataset_name].append(variable_name)
        return datasets

    @classmethod
    def get_all_configs(cls):
        return {x.NAME: x for x in cls._get_list_of_configs()}

    @classmethod
    def get_config(cls, config_name):
        return cls.get_all_configs()[config_name]

    @classmethod
    def _get_list_of_configs(cls):
        list_of_configs = cls.__subclasses__()
        for subclass in cls.__subclasses__():
            list_of_configs += subclass._get_list_of_configs()
        return list_of_configs
