import pytest

from studies.models import Study
from workspace.models import Basket, BasketVariable, Script

from .factories import ScriptFactory

pytestmark = [pytest.mark.workspace]


@pytest.fixture
def script(db):
    """ A script in the database """
    return ScriptFactory(name="some-script", label="Some Script")


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

    def test_get_or_create_method(self):
        pass

    def test_get_script_generators_method(self, basket):
        result = basket.get_script_generators()
        assert result is None

    def test_get_script_generators_method_with_config(self, mocker, basket):
        mocked_get_config = mocker.patch.object(Study, "get_config")
        mocked_get_config.return_value = {"script_generators": "some-script-generator"}
        result = basket.get_script_generators()
        assert result == "some-script-generator"

    def test_to_csv_method(self, mocker, basket, variable):
        pass


class TestScriptModel:
    def test_get_config_method(self):
        pass

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
