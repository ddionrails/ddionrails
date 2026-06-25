# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for scripts in ddionrails.workspace app"""

import json
from unittest.mock import patch

import factory
from django.test import TestCase
from factory.django import DjangoModelFactory

from ddionrails.workspace.models import BasketVariable
from ddionrails.workspace.models.script import Script
from ddionrails.workspace.models.script_metadata import ScriptMetadata
from ddionrails.workspace.scripts import ScriptConfig, SoepR, SoepSpss, SoepStata
from tests.model_factories import BasketFactory, StudyFactory, VariableFactory

STATA_HEADING_GENDER = "* * * GENDER ( male = 1 / female = 2) * * *"
SPSS_R_HEADING_GENDER = "### GENDER ( male = 1 / female = 2) ###"


class ScriptFactory(DjangoModelFactory):
    class Meta:
        model = Script

    basket = factory.SubFactory(BasketFactory)
    settings = factory.LazyAttribute(lambda _: '{"analysis_unit": "p"}')


class TestScriptConfig_(TestCase):

    def test_get_script_input_method(self):
        basket = BasketFactory()
        script = ScriptFactory(basket=basket)
        script_config = ScriptConfig(script, basket)
        get_script_input_patch = patch.object(ScriptConfig, "get_datasets_and_variables")
        mocked_get_script_input = get_script_input_patch.start()
        mocked_get_script_input.return_value = {}
        script_config.template = "some-template.html"
        result = script_config.get_script_input()
        self.assertEqual(result["template"], script_config.template)
        self.assertEqual(result["settings"], json.loads(script_config.script.settings))
        self.assertEqual(result["data"], {})
        get_script_input_patch.stop()

    def test_get_datasets_and_variables_method(self):
        basket = BasketFactory()
        script = ScriptFactory(basket=basket)
        script_config = ScriptConfig(script, basket)
        variable = VariableFactory(dataset__study=basket.study)

        basket_variable = BasketVariable(basket=script_config.basket, variable=variable)
        basket_variable.save()
        result = script_config.get_datasets_and_variables()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[variable.dataset.name], [variable.name])

    def test_get_config_method(self):
        config_name = "some-config-name"
        config = "some-config"
        get_all_configs_patch = patch.object(ScriptConfig, "get_all_configs")

        mocked_get_all_configs = get_all_configs_patch.start()

        mocked_get_all_configs.return_value = {config_name: config}
        result = ScriptConfig.get_config(config_name)
        self.assertEqual(result, config)


SCRIPT_METADATA = {
    "dataset_name": "",
    "syear": "",
    "prefix": "",
    "analysis_unit": "",
    "is_matchable": "",
    "curr_hid": "",
    "is_special": "",
}


class TestSoepStata(TestCase):

    def setUp(self) -> None:
        study = StudyFactory(name="soep-core")
        basket = BasketFactory(study=study)

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()
        self.script_metadata = metadata_object
        script = ScriptFactory(basket=basket)
        self.soepstata = SoepStata(script, basket)
        return super().setUp()

    def test_render_individual_gender_method_with_male(self):
        self.soepstata.settings["gender"] = "m"
        self.soepstata.settings["analysis_unit"] = "p"
        result = self.soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 1)"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_female(self):
        self.soepstata.settings["gender"] = "f"
        self.soepstata.settings["analysis_unit"] = "p"
        result = self.soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 2)"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_both(self):
        self.soepstata.settings["gender"] = "b"
        self.soepstata.settings["analysis_unit"] = "p"
        result = self.soepstata._render_gender()  # pylint: disable=protected-access
        command = "\n/* all genders */"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_render_household_gender_method_with_both(self):
        self.soepstata.settings["gender"] = "b"
        self.soepstata.settings["analysis_unit"] = "h"
        result = self.soepstata._render_gender()  # pylint: disable=protected-access
        assert "\n\n* * * GENDER NOT FOR HOUSEHOLDS * * *\n" in result

    def test_disclaimer(self):
        result = self.soepstata._render_disclaimer()  # pylint: disable=protected-access
        expected = (
            "\n"
            "* --------------------------------------------------------------------.\n"
            "* This command file was generated by paneldata.org                    .\n"
            "* --------------------------------------------------------------------.\n"
            "* !!! I M P O R T A N T - W A R N I N G !!!                           .\n"
            "* You alone are responsible for contents and appropriate.             .\n"
            "* usage by accepting the usage agreement.                             .\n"
            "* --------------------------------------------------------------------.\n"
            "* Please report any errors of the code generated here                 .\n"
            "* to soepmail@diw.de                                                  .\n"
            "* --------------------------------------------------------------------.\n"
        )
        assert expected == result

    def test_render_sort_pfad(self):
        result = self.soepstata._render_sort_pfad()  # pylint: disable=protected-access
        expected = (
            "\n\n"
            "* * * SAVE PFAD * * *\n\n"
            'save "${MY_PATH_OUT}pfad.dta", replace \nclear'
        )
        assert expected == result

    def test_render_done(self):
        result = self.soepstata._render_done()  # pylint: disable=protected-access
        expected = (
            "\n\n"
            "* * * DONE * * *\n\n"
            'label data "paneldata.org"\n'
            'save "${MY_FILE_OUT}", replace\n'
            "desc\n\n"
            "log close"
        )
        assert expected == result


class TestSoepSpssClass(TestCase):

    def setUp(self) -> None:
        study = StudyFactory(name="soep-core")
        basket = BasketFactory(study=study)

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()
        self.script_metadata = metadata_object
        script = ScriptFactory(basket=basket)
        self.soepspss = SoepSpss(script, basket)
        return super().setUp()

    def test_render_individual_gender_method_with_male(self):
        self.soepspss.settings["gender"] = "m"
        self.soepspss.settings["analysis_unit"] = "p"
        result = self.soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex = 1)"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_female(self):
        self.soepspss.settings["gender"] = "f"
        self.soepspss.settings["analysis_unit"] = "p"
        result = self.soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex = 2)"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_both(self):
        self.soepspss.settings["gender"] = "b"
        self.soepspss.settings["analysis_unit"] = "p"
        result = self.soepspss._render_gender()  # pylint: disable=protected-access
        command = "\n* all genders *."
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_household_gender_method_with_both(self):
        self.soepspss.settings["gender"] = "b"
        self.soepspss.settings["analysis_unit"] = "h"
        result = self.soepspss._render_gender()  # pylint: disable=protected-access
        assert "\n* ### GENDER NOT FOR HOUSEHOLDS ### *.\n" in result

    def test_render_done(self):
        result = self.soepspss._render_done()  # pylint: disable=protected-access
        expected = (
            "\n"
            "* ### DONE ### *.\n\n"
            "dataset close all.\n"
            "dataset name new.\n"
            "dataset activate new.\n"
            'file label "paneldata.org".\n'
            "save outfile = !pathout+'new.sav'.\n"
            "desc all."
        )
        assert expected == result


class TestSoepR(TestCase):

    def setUp(self) -> None:
        study = StudyFactory(name="soep-core")
        basket = BasketFactory(study=study)

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()
        self.script_metadata = metadata_object
        script = ScriptFactory(basket=basket)
        self.soepr = SoepR(script, basket)
        return super().setUp()

    def test_render_individual_gender_method_with_male(self):
        self.soepr.settings["gender"] = "m"
        self.soepr.settings["analysis_unit"] = "p"
        result = self.soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==1,]"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_female(self):
        self.soepr.settings["gender"] = "f"
        self.soepr.settings["analysis_unit"] = "p"
        result = self.soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==2,]"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_individual_gender_method_with_both(self):
        self.soepr.settings["gender"] = "b"
        self.soepr.settings["analysis_unit"] = "p"
        result = self.soepr._render_gender()  # pylint: disable=protected-access
        command = "\n# all genders"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_household_gender_method_with_both(self):
        self.soepr.settings["gender"] = "b"
        self.soepr.settings["analysis_unit"] = "h"
        result = self.soepr._render_gender()  # pylint: disable=protected-access
        assert "\n### GENDER NOT FOR HOUSEHOLDS ###\n" in result

    def test_render_done(self):
        result = self.soepr._render_done()  # pylint: disable=protected-access
        expected = (
            "\n"
            "### DONE ###\n\n"
            'attr(main, "label") <- "paneldata.org"\n'
            "str(main)\n"
            'save(main, file=file.path(path_out, "main.RData"))'
        )
        assert expected == result
