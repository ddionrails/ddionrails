import pytest
from django.http.response import Http404
from django.urls import reverse

from elastic.mixins import ModelMixin
from studies.views import StudyDetailView, StudyRedirectView, study_topics

pytestmark = [pytest.mark.studies, pytest.mark.views]


class TestStudyRedirectView:
    def test_study_redirect(self, rf, study):
        request = rf.get("study", kwargs={"pk": study.pk})
        response = StudyRedirectView.as_view()(request, id=study.pk)
        assert response.status_code == 302

    def test_study_redirect_invalid_id(self, rf, study):
        invalid_study_id = 999
        request = rf.get("study", kwargs={"pk": invalid_study_id})
        with pytest.raises(Http404):
            StudyRedirectView.as_view()(request, id=invalid_study_id)


class TestStudyDetailView:
    def test_study_detail_view_with_existing_study_pk(self, mocker, client, study):
        mocked_get_source = mocker.patch.object(ModelMixin, "get_source")
        mocked_get_source.return_value = dict()

        url = reverse("study_detail", kwargs={"study_name": study.name})
        response = client.get(url)
        assert response.status_code == 200
        template = "studies/study_detail.html"
        assert template in (t.name for t in response.templates)
        # # TODO
        assert "debug_string" in response.context
        assert response.context["study"] == study
        expected_datasets = list(study.datasets.all())
        output_datasets = list(response.context["dataset_list"])
        assert expected_datasets == output_datasets
        expected_instruments = list(study.instruments.all())
        output_instruments = list(response.context["instrument_list"])
        assert expected_instruments == output_instruments

    def test_study_detail_view_with_non_existing_study_name(self, rf, db):
        non_existing_study_name = "not-in-database"
        url = reverse("study_detail", kwargs={"study_name": non_existing_study_name})
        request = rf.get(url)
        with pytest.raises(Http404):
            StudyDetailView.as_view()(request, study_name=non_existing_study_name)


# class TestStudyTopicsView:
#     def test_study_topics_view_with_existing_study_name(self, rf, study):
#         url = reverse("study.topics", kwargs={"study_name": study.name})
#         request = rf.get(url)
#         response = study_topics(request, study_name=study.name)
#         assert response.status_code == 200
#         # TODO: assert topics
#         # TODO: assert template
#
#     def test_study_topics_view_with_non_existing_study_name(self, rf, db):
#         non_existing_study_name = "not-in-database"
#         url = reverse("study.topics", kwargs={"study_name": non_existing_study_name})
#         request = rf.get(url)
#         with pytest.raises(Http404):
#             study_topics(request, study_name=non_existing_study_name)
