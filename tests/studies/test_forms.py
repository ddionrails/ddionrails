import pytest

from ddionrails.studies.forms import StudyForm, StudyInitialForm

pytestmark = [pytest.mark.studies, pytest.mark.form]


class TestStudyForm:
    def test_form_without_data(self, empty_data):
        form = StudyForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, db):
        valid_study_data = dict(
            name="some-study", label="Some Study", description="This is some study"
        )
        form = StudyForm(data=valid_study_data)
        assert form.is_valid() is True
        study = form.save()
        assert study.name == valid_study_data["name"]


class TestStudyInitialForm:
    def test_form_without_data(self):
        invalid_data = dict(name="")
        form = StudyInitialForm(data=invalid_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, db):
        valid_study_data = dict(name="some-study")
        form = StudyInitialForm(data=valid_study_data)
        assert form.is_valid() is True
        study = form.save()
        assert study.name == valid_study_data["name"]
