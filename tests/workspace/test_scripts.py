import json

import pytest

from workspace.scripts import ScriptConfig, SoepMixin, SoepR, SoepSpss, SoepStata
from workspace.models import BasketVariable


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
        result = ScriptConfig.get_all_configs()

    def test_get_config_method(self, mocker):
        config_name = "some-config-name"
        config = "some-config"
        mocked_get_all_configs = mocker.patch.object(ScriptConfig, "get_all_configs")
        mocked_get_all_configs.return_value = {config_name: config}
        result = ScriptConfig.get_config(config_name)
        assert result == config

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_get_list_of_configs_method(self):
        result = ScriptConfig._get_list_of_configs()


class TestSoepMixin:
    pass


class TestSoepStataClass:
    def test_render_gender_method_with_male(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "m"
        result = soepstata._render_gender()
        command = "keep if (sex == 1)"
        assert heading_stata in result
        assert command in result

    def test_render_gender_method_with_female(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "f"
        result = soepstata._render_gender()
        command = "keep if (sex == 2)"
        assert heading_stata in result
        assert command in result

    def test_render_gender_method_with_both(self, soepstata, heading_stata):
        soepstata.settings["gender"] = "b"
        result = soepstata._render_gender()
        command = "\n/* all genders */"
        assert heading_stata in result
        assert command in result


class TestSoepSpssClass:
    def test_render_gender_method_with_male(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "m"
        result = soepspss._render_gender()
        command = "select if (sex == 1)"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_female(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "f"
        result = soepspss._render_gender()
        command = "select if (sex == 2)"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_both(self, soepspss, heading_spss_r):
        soepspss.settings["gender"] = "b"
        result = soepspss._render_gender()
        command = "\n* all genders *."
        assert heading_spss_r in result
        assert command in result


class TestSoepRClass:
    def test_render_gender_method_with_male(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "m"
        result = soepr._render_gender()
        command = "pfad <- pfad[pfad$sex==1,]"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_female(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "f"
        result = soepr._render_gender()
        command = "pfad <- pfad[pfad$sex==2,]"
        assert heading_spss_r in result
        assert command in result

    def test_render_gender_method_with_both(self, soepr, heading_spss_r):
        soepr.settings["gender"] = "b"
        result = soepr._render_gender()
        command = "\n# all genders"
        assert heading_spss_r in result
        assert command in result
