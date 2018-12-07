import pytest

from studies.models import Study
from workspace.models import Script, Basket, BasketVariable, ScriptConfig

from .factories import ScriptFactory


pytestmark = [pytest.mark.workspace]


@pytest.fixture
def script(db):
    """ A script in the database """
    return ScriptFactory(name="some-script", label="Some Script")


@pytest.fixture
def csv_heading(db):
    return "name,label,label_de,dataset_name,dataset_label,dataset_label_de,study_name,study_label,study_label_de,concept_name,period_name"


class TestBasketModel:
    def test_string_method(self, basket):
        assert str(basket) == basket.user.username + "/" + basket.name

    def test_absolute_url_method(self, basket):
        expected = f"/workspace/baskets/{basket.id}"
        assert basket.get_absolute_url() == expected

    def test_html_description_method(self, mocker, basket):
        mocked_render_markdown = mocker.patch("workspace.models.render_markdown")
        basket.html_description()
        mocked_render_markdown.assert_called_once()

    def test_title_method(self, basket):
        assert basket.title() == basket.name

    def test_title_method_with_label(self, basket):
        basket.label = "Some basket"
        assert basket.title() == basket.label

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_get_or_create_method(self, user):
        basket = Basket.get_or_create("some-basket", user.username)
        assert basket

    def test_get_script_generators_method(self, basket):
        result = basket.get_script_generators()
        assert result is None

    def test_get_script_generators_method_with_config(self, mocker, basket):
        mocked_get_config = mocker.patch.object(Study, "get_config")
        mocked_get_config.return_value = {"script_generators": "some-script-generator"}
        result = basket.get_script_generators()
        assert result == "some-script-generator"

    def test_to_csv_method_with_empty_basket(self, basket, csv_heading):
        result = basket.to_csv()
        assert csv_heading in result

    def test_to_csv_method_with_variable_in_basket(self, basket, variable, csv_heading):
        basket_variable = BasketVariable(basket=basket, variable=variable)
        basket_variable.save()
        result = basket.to_csv()
        assert csv_heading in result
        assert variable.name in result
        assert variable.label in result
        assert variable.dataset.name in result
        assert variable.dataset.study.name in result

    def test_to_csv_method_with_variable_and_concept_in_basket(
        self, basket, variable, concept, csv_heading
    ):
        concept.variables.add(variable)
        basket_variable = BasketVariable(basket=basket, variable=variable)
        basket_variable.save()
        result = basket.to_csv()
        assert csv_heading in result
        assert variable.name in result
        assert variable.label in result
        assert variable.dataset.name in result
        assert variable.dataset.study.name in result
        assert variable.concept.name in result


class TestScriptModel:
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_get_config_method(self, mocker, script):
        mocked_get_config = mocker.patch.object(ScriptConfig, "get_config")
        # mocked_get_config.return_value = dict(key="value")
        result = script.get_config()
        assert result

    def test_get_config_method_with_local_config(self, script):
        script.local_config = "local-config"
        result = script.get_config()
        assert result == script.local_config

    def test_get_settings_method(self, script):
        script.settings_dict = dict(key="value")
        result = script.get_settings()
        assert result["key"] == "value"

    def test_get_settings_method_without_settings_dict(self, script):
        script.settings = '{"key": "value"}'
        result = script.get_settings()
        assert result["key"] == "value"

    def test_get_script_input_method(self, mocker, script):
        mocked_get_config = mocker.patch.object(Script, "get_config")
        script.get_script_input()
        mocked_get_config.assert_called_once()

    def test_title_method(self, script):
        script.label = ""
        assert script.title() == script.name

    def test_title_method_with_label(self, script):
        assert script.title() == script.label

    def test_string_method(self, script):
        expected = f"/workspace/baskets/{script.basket.id}/scripts/{script.id}"
        assert str(script) == expected

    def test_absolute_url_method(self, script):
        expected = f"/workspace/baskets/{script.basket.id}/scripts/{script.id}"
        assert script.get_absolute_url() == expected
