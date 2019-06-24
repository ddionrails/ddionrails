# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for scripts in ddionrails.workspace app """

import json

import pytest

from ddionrails.workspace.models import BasketVariable
from ddionrails.workspace.scripts import (
    ScriptConfig,
    SoepMixin,
    SoepR,
    SoepSpss,
    SoepStata,
)


@pytest.fixture
def soepstata(script, basket):
    return SoepStata(script, basket)


@pytest.fixture
def heading_stata():
    return "* * * GENDER ( male = 1 / female = 2) * * *"


@pytest.fixture
def soepspss(script, basket):
    return SoepSpss(script, basket)


@pytest.fixture
def heading_spss_r():
    return "### GENDER ( male = 1 / female = 2) ###"


@pytest.fixture
def soepr(script, basket):
    return SoepR(script, basket)


@pytest.fixture
def script_config(script, basket):
    return ScriptConfig(script, basket)


@pytest.fixture
def soepmixin():
    return SoepMixin()


@pytest.fixture
def soepletters():
    return [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "ba",
        "bb",
        "bc",
        "bd",
        "be",
        "bf",
        "bg",
    ]


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

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_get_all_configs_method(self, mocker):
        mocked_get_list_of_configs = mocker.patch.object(
            ScriptConfig, "_get_list_of_configs"
        )
        ScriptConfig.get_all_configs()

    def test_get_config_method(self, mocker):
        config_name = "some-config-name"
        config = "some-config"
        mocked_get_all_configs = mocker.patch.object(ScriptConfig, "get_all_configs")
        mocked_get_all_configs.return_value = {config_name: config}
        result = ScriptConfig.get_config(config_name)
        assert result == config


testdata_soep_classify_dataset_method = [("ah", "h"), ("ap", "p")]


class TestSoepMixin:
    def test_soep_year_method(self, soepmixin):
        year = 2001
        soepmixin._soep_year(year)  # pylint: disable=protected-access

    def test_soep_letters_method(self, soepmixin, soepletters):
        result = soepmixin._soep_letters()  # pylint: disable=protected-access
        assert result == soepletters

    def test_soep_letters_method_page_1(self, soepmixin):
        page = 1
        result = soepmixin._soep_letters(page)
        assert result == [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]

    def test_soep_letters_method_page_2(self, soepmixin):
        page = 2
        result = soepmixin._soep_letters(page)  # pylint: disable=protected-access
        assert result == ["ba", "bb", "bc", "bd", "be", "bf", "bg"]

    @pytest.mark.parametrize("input,expected", testdata_soep_classify_dataset_method)
    def test_soep_classify_dataset_method(
        self, mocker, soepmixin, soepletters, input, expected
    ):
        mocked_soep_letters = mocker.patch.object(SoepMixin, "_soep_letters")
        mocked_soep_letters.return_value = soepletters
        dataset_name = input
        result = soepmixin._soep_classify_dataset(
            dataset_name
        )  # pylint: disable=protected-access
        assert result == expected

    def test_soep_letter_year_method(self):
        pass

    def test_soep_get_year_method(self):
        pass

    def test_generate_script_dict_method(self):
        pass

    def test_create_dataset_dict_method(self):
        pass

    def test_enrich_dataset_dict_method(self):
        pass

    def test_validate_datasets_method(self):
        pass

    def test_get_selected_years_method(self):
        pass


class TestSoepStataClass:
    def test_init_method(self):
        pass

    def test_get_script_input_method(self):
        pass

    def test_render_disclaimer_method(self):
        pass

    def test_render_local_variables_method(self):
        pass

    def test_render_not_processed_method(self):
        pass

    def test_render_pfad_method(self):
        pass

    def test_render_balanced_method(self):
        pass

    def test_render_private_method(self):
        pass

    def test_render_sort_pfad_method(self):
        pass

    def test_render_hrf_method(self):
        pass

    def test_render_create_master_method(self):
        pass

    def test_render_read_data_method(self):
        pass

    def test_render_merge_method(self):
        pass

    def test_render_done_method(self):
        pass

    def test_render_gender_method_with_male(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "m"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 1)"
        assert heading_stata in result
        assert command in result

    def test_render_gender_method_with_female(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "f"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "keep if (sex == 2)"
        assert heading_stata in result
        assert command in result

    def test_render_gender_method_with_both(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "b"
        result = soepstata._render_gender()  # pylint: disable=protected-access
        command = "\n/* all genders */"
        assert heading_stata in result
        assert command in result


class TestSoepSpssClass:
    def test_render_local_variables_method(self):
        pass

    def test_render_pfad_method(self):
        pass

    def test_render_balanced_method(self):
        pass

    def test_render_private_method(self):
        pass

    def test_render_gender_method_with_male(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "m"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex == 1)"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_female(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "f"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "select if (sex == 2)"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_both(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "b"
        result = soepspss._render_gender()  # pylint: disable=protected-access
        command = "\n* all genders *."
        assert heading_spss_r in result
        assert command in result


class TestSoepRClass:
    def test_render_gender_method_with_male(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "m"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==1,]"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_female(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "f"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "pfad <- pfad[pfad$sex==2,]"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_both(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "b"
        result = soepr._render_gender()  # pylint: disable=protected-access
        command = "\n# all genders"
        assert heading_spss_r in result
        assert command in result
