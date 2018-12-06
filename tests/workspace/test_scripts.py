import pytest

from workspace.scripts import SoepStata


@pytest.fixture
def soepstata(script, basket):
    return SoepStata(script, basket)


@pytest.fixture
def heading():
    return "* * * GENDER ( male = 1 / female = 2) * * *"


class TestSoepStataClass:
    def test_render_gender_method_with_male(self, soepstata, heading):
        soepstata.settings["gender"] = "m"
        result = soepstata._render_gender()
        command = "keep if (sex == 1)"
        assert heading in result
        assert command in result

    def test_render_gender_method_with_female(self, soepstata, heading):
        soepstata.settings["gender"] = "f"
        result = soepstata._render_gender()
        command = "keep if (sex == 2)"
        assert heading in result
        assert command in result

    def test_render_gender_method_with_both(self, soepstata, heading):
        soepstata.settings["gender"] = "b"
        result = soepstata._render_gender()
        command = "\n/* all genders */"
        assert heading in result
        assert command in result
