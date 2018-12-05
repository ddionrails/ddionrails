import pytest
from django.http.response import Http404
from django.urls import reverse

from instruments.views import InstrumentDetailView, InstrumentRedirectView, QuestionRedirectView


@pytest.mark.django_db
class TestInstrumentDetailView:
    def test_detail_view_with_existing_names(self, client, instrument):
        url = reverse(
            "inst:instrument_detail", kwargs={"study_name": instrument.study.name, "instrument_name": instrument.name}
        )
        response = client.get(url)
        assert response.status_code == 200
        template = "instruments/instrument_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["instrument"] == instrument
        assert response.context["study"] == instrument.study
        expected_questions = list(instrument.questions.select_subclasses().all())
        output_questions = list(response.context["questions"])
        assert expected_questions == output_questions

    def test_detail_view_with_invalid_study_name(self):
        pass

    def test_detail_view_with_invalid_instrument_name(self):
        pass


@pytest.mark.django_db
class TestInstrumentRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, instrument):
        url = reverse("instrument_redirect", kwargs={"id": 1})
        request = rf.get(url)
        response = InstrumentRedirectView.as_view()(request, id=1)
        assert response.status_code == 302

    def test_redirect_view_with_invalid_pk(self, db, rf):
        invalid_pk = 999
        request = rf.get("instrument_redirect", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            InstrumentRedirectView.as_view()(request, id=invalid_pk)


@pytest.mark.django_db
class TestQuestionRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, question):
        url = reverse("question_redirect", kwargs={"id": 1})
        request = rf.get(url)
        response = QuestionRedirectView.as_view()(request, id=1)
        assert response.status_code == 302

    def test_redirect_view_with_invalid_pk(self, db, rf):
        invalid_pk = 999
        request = rf.get("question_redirect", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            QuestionRedirectView.as_view()(request, id=invalid_pk)
