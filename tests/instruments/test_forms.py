from instruments.forms import InstrumentForm, QuestionForm


class TestInstrumentForm:
    def test_form_with_invalid_data(self, invalid_instrument_data):
        form = InstrumentForm(data=invalid_instrument_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, valid_instrument_data):
        form = InstrumentForm(data=valid_instrument_data)
        assert form.is_valid() is True
        instrument = form.save()
        assert instrument.name == valid_instrument_data["instrument_name"]

    def test_form_with_valid_data_with_other_keys(self, study):
        valid_instrument_data = dict(
            instrument_name="some-instrument",
            study_name=study.name
        )
        form = InstrumentForm(data=valid_instrument_data)
        assert form.is_valid() is True
        instrument = form.save()
        assert instrument.name == valid_instrument_data["instrument_name"]

class TestQuestionForm:
    def test_form_with_invalid_data(self, invalid_question_data):
        form = QuestionForm(data=invalid_question_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, valid_question_data):
        form = QuestionForm(data=valid_question_data)
        assert form.is_valid() is True
        question = form.save()
        assert question.name == valid_question_data['question_name']

    def test_form_with_valid_data_with_other_keys(self, study, instrument):
        valid_question_data = dict(
            question_name='some-question',
            instrument_name=instrument.name,
            study_name=study.name,
        )
        form = QuestionForm(data=valid_question_data)
        assert form.is_valid() is True
        assert form.data['instrument_object'] == instrument
        question = form.save()
        assert question.name == valid_question_data['question_name']
