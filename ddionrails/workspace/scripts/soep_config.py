# -*- coding: utf-8 -*-

""" Config """

import json

from ..mixins import SoepMixin
from .script_config import ScriptConfig

class SoepConfig(ScriptConfig, SoepMixin):
    """ Prepare UI """

    DEFAULT_DICT = dict(
        path_in="data/",
        path_out="out/",
        analysis_unit="p",
        private="t",
        gender="b",
        balanced="t",
        age_group="adult",
    )
    DEFAULT_CONFIG = json.dumps(DEFAULT_DICT)

    def __init__(self, script, basket):
        self.basket = basket
        self.script = script
        self.fields = [
            dict(name="path_in", label="Input path", scale="text"),
            dict(name="path_out", label="Output path", scale="text"),
            dict(
                name="analysis_unit",
                label="Analysis Unit",
                scale="select",
                options=dict(p="Individual", h="Household"),
            ),
            dict(
                name="private",
                label="Private households",
                scale="select",
                options=dict(t="Only private households", f="All households"),
            ),
            dict(
                name="gender",
                label="Gender",
                scale="select",
                options=dict(b="Both", m="Male", f="Female"),
            ),
            dict(
                name="balanced",
                label="Sample composition",
                scale="select",
                options=dict(t="balanced", f="unbalanced"),
            ),
            dict(
                name="age_group",
                label="Age group",
                scale="select",
                options=dict(
                    all="All sample members",
                    adult="All adult respondents",
                    no17="All adult repspondents without first time interviewed (age 17)",
                ),
            ),
        ]
        # get_settings reads a JSON in script.py containing all settings in basket (databank)
        self.settings = script.get_settings()
        self.template = "scripts/soep_stata.html"
        # script_dict_raw is a dict created in mixins.py containing the dataset with all variables and infos from basket
        self.script_dict_raw = self._generate_script_dict()
        # valid_datasets contains all valid datasets from the basket
        valid_datasets = self._validate_datasets(
            self.script_dict_raw, self.settings["analysis_unit"]
        )
        # script_dict contains all datasets and variables that are valid in the basket
        self.script_dict = {
            x: y for x, y in self.script_dict_raw.items() if x in valid_datasets
        }
        # years contains the prefixes of all years, including in the basket
        self.years = set([d["prefix"] for d in self.script_dict.values() if d["prefix"] != ""])