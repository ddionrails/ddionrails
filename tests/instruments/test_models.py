import pytest

pytestmark = [pytest.mark.instrument, pytest.mark.models]


class TestInstrumentModel:
    def test_string_method(self, instrument, study):
        assert str(instrument) == "/" + study.name + "/inst/" + instrument.name

    def test_get_absolute_url_method(self, instrument, study):
        assert (
            instrument.get_absolute_url() == "/" + study.name + "/inst/" + instrument.name
        )


class TestQuestionModel:
    def test_string_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert str(question) == expected

    def test_get_absolute_url_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert question.get_absolute_url() == expected

    def test_layout_class_method(self, question):
        expected = "question"
        assert question.layout_class() == expected

    def test_get_answers_method(self):
        pass

    def test_previous_question_method(self):
        pass

    def test_next_question_method(self):
        pass

    def test_concept_list_method(self):
        pass

    def test_get_cs_name_method(self):
        pass

    def test_title_method(self, question):
        assert question.title() == question.label

    def test_title_method_without_label(self, question):
        question.label = ""
        assert question.title() == question.name

    def test_translation_languages_method(self):
        pass

    def test_translate_item_method(self):
        pass

    def test_translations_method(self):
        pass

    def test_item_array_method(self):
        pass
