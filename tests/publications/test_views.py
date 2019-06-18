# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.publications app """

import pytest
from django.http.response import Http404
from django.urls import reverse

from ddionrails.elastic.mixins import ModelMixin
from ddionrails.publications.views import PublicationRedirectView


class TestPublicationRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, publication):
        request = rf.get("publication", kwargs={"pk": publication.pk})
        response = PublicationRedirectView.as_view()(request, id=publication.pk)
        assert response.status_code == 302

    def test_redirect_view_with_invalid_pk(self, rf, publication):
        invalid_dataset_id = 999
        request = rf.get("study", kwargs={"pk": invalid_dataset_id})
        with pytest.raises(Http404):
            PublicationRedirectView.as_view()(request, id=invalid_dataset_id)


class TestPublicationDetailView:
    def test_detail_view_with_existing_names(self, mocker, client, publication):
        # TODO return_value
        mocked_get_source = mocker.patch.object(ModelMixin, "get_source")
        mocked_get_source.return_value = dict()
        url = reverse(
            "publ:publication",
            kwargs={
                "study_name": publication.study.name,
                "publication_name": publication.name,
            },
        )
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_detail_view_with_invalid_study_name(self, mocker, client, publication):
        # TODO return_value
        mocked_get_source = mocker.patch.object(ModelMixin, "get_source")
        mocked_get_source.return_value = dict()
        url = reverse(
            "publ:publication",
            kwargs={
                "study_name": "invalid-study-name",
                "publication_name": publication.name,
            },
        )
        # TODO raise 404?
        response = client.get(url)
        assert response.status_code == 404
        # class 'django.http.response.HttpResponseNotFound'>

    def test_detail_view_with_invalid_dataset_name(self, client, dataset):
        pass


class TestStudyPublicationListView:
    pass
