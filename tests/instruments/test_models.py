import pytest

pytestmark = [pytest.mark.instrument, pytest.mark.models]


class TestInstrumentModel:
    def test_string_method(self, instrument, study):
        assert str(instrument) == "/" + study.name + "/inst/" + instrument.name

    def test_get_absolute_url_method(self, instrument, study):
        assert instrument.get_absolute_url() == "/" + study.name + "/inst/" + instrument.name


class TestQuestionModel:
    def test_string_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert str(question) == expected

    def test_get_absolute_url_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert question.get_absolute_url() == expected
