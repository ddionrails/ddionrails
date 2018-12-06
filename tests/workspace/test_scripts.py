import pytest

from workspace.scripts import SoepStata
from workspace.scripts import SoepSpss

### Stata Settings

@pytest.fixture
def soepstata(script, basket):
    return SoepStata(script, basket)

@pytest.fixture
def heading_stata():
    return "* * * GENDER ( male = 1 / female = 2) * * *"
    
### SPSS Settings

@pytest.fixture
def soepspss(script, basket):
    return SoepSpss(script, basket)

@pytest.fixture
def heading_spss():
    return "### GENDER ( male = 1 / female = 2) ###"


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
    def test_render_gender_method_with_male(self, soepspss, heading_spss):
        soepspss.settings["gender"] = "m"
        result = soepspss._render_gender()
        command = "select if (sex == 1)"
        assert heading_spss in result
        assert command in result

    def test_render_gender_method_with_female(self, soepspss, heading_spss):
        soepspss.settings["gender"] = "f"
        result = soepspss._render_gender()
        command = "select if (sex == 2)"
        assert heading_spss in result
        assert command in result

    def test_render_gender_method_with_both(self, soepspss, heading_spss):
        soepspss.settings["gender"] = "b"
        result = soepspss._render_gender()
        command = "\n* all genders *."
        assert heading_spss in result
        assert command in result
