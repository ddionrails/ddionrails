# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for scripts in ddionrails.workspace app """

import json

import pytest

from ddionrails.workspace.models import BasketVariable
from ddionrails.workspace.scripts import ScriptConfig, SoepR, SoepSpss, SoepStata


@pytest.fixture
def soepstata(script, basket):
    """ An instantiated SoepStata object with related script and basket """
    return SoepStata(script, basket)


@pytest.fixture
def soepspss(script, basket):
    """ An instantiated SoepSpss object with related script and basket """
    return SoepSpss(script, basket)


@pytest.fixture
def soepr(script, basket):
    """ An instantiated SoepR object with related script and basket """
    return SoepR(script, basket)


@pytest.fixture
def script_config(script, basket):
    """ An instantiated ScriptConfig object with related script and basket """
    return ScriptConfig(script, basket)


STATA_HEADING_GENDER = "* * * GENDER ( male = 1 / female = 2) * * *"
SPSS_R_HEADING_GENDER = "### GENDER ( male = 1 / female = 2) ###"


class TestScriptConfig:
    def test_get_script_input_method(self, mocker, script_config):
        mocked_get_script_input = mocker.patch.object(
            ScriptConfig, "get_datasets_and_variables"
        )
        mocked_get_script_input.return_value = dict()
        script_config.template = "some-template.html"
        result = script_config.get_script_input()
        assert result["template"] == script_config.template
        assert result["settings"] == json.loads(script_config.script.settings)
        assert result["data"] == dict()

    def test_get_datasets_and_variables_method(self, script_config, variable):
        # Add variable to basket
        basket_variable = BasketVariable(basket=script_config.basket, variable=variable)
        basket_variable.save()
        result = script_config.get_datasets_and_variables()
        assert len(result) == 1
        assert result[variable.dataset.name] == [variable.name]

    def test_get_config_method(self, mocker):
        config_name = "some-config-name"
        config = "some-config"
        mocked_get_all_configs = mocker.patch.object(ScriptConfig, "get_all_configs")
        mocked_get_all_configs.return_value = {config_name: config}
        result = ScriptConfig.get_config(config_name)
        assert result == config


class TestSoepStata:
    def test_render_gender_method_with_male(self, soepstata):
        soepstata.settings["gender"] = "m"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 1)"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_female(self, soepstata):
        soepstata.settings["gender"] = "f"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 2)"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_both(self, soepstata):
        soepstata.settings["gender"] = "b"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "\n/* all genders */"
        assert STATA_HEADING_GENDER in result
        assert command in result

    def test_disclaimer(self, soepstata):
        result = soepstata._render_disclaimer()  # pylint: disable=protected-access
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

    def test_render_sort_pfad(self, soepstata):
        result = soepstata._render_sort_pfad()  # pylint: disable=protected-access
        expected = (
            "\n\n" "* * * SORT PFAD * * *\n\n" 'save "${MY_PATH_OUT}pfad.dta", replace'
        )
        assert expected == result

    def test_render_done(self, soepstata):
        result = soepstata._render_done()  # pylint: disable=protected-access
        expected = (
            "\n\n"
            "* * * DONE * * *\n\n"
            'label data "paneldata.org: Magic at work!"\n'
            'save "${MY_FILE_OUT}", replace\n'
            "desc\n\n"
            "log close"
        )
        assert expected == result


class TestSoepSpssClass:
    def test_render_gender_method_with_male(self, soepspss):
        soepspss.settings["gender"] = "m"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex == 1)"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_female(self, soepspss):
        soepspss.settings["gender"] = "f"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex == 2)"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_both(self, soepspss):
        soepspss.settings["gender"] = "b"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "\n* all genders *."
        assert SPSS_R_HEADING_GENDER in result
        assert command in result


class TestSoepR:
    def test_render_gender_method_with_male(self, soepr):
        soepr.settings["gender"] = "m"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==1,]"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_female(self, soepr):
        soepr.settings["gender"] = "f"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==2,]"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_gender_method_with_both(self, soepr):
        soepr.settings["gender"] = "b"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "\n# all genders"
        assert SPSS_R_HEADING_GENDER in result
        assert command in result

    def test_render_done(self, soepr):
        result = soepr._render_done()  # pylint: disable=protected-access
        expected = (
            "\n"
            "### DONE ###\n\n"
            'attr(master, "label") <- "paneldata.org: Magic at work!"\n'
            "str(master)\n"
            'save(master, file=file.path(path_out, "master.RData"))'
        )
        assert expected == result
