# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.publications app """

import pytest
from django.http.response import Http404
from django.urls import reverse

from ddionrails.publications.views import PublicationRedirectView
from tests import status


class TestPublicationRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, publication):
        request = rf.get("publication", kwargs={"pk": publication.pk})
        response = PublicationRedirectView.as_view()(request, id=publication.pk)
        assert status.HTTP_302_FOUND == response.status_code

    @pytest.mark.django_db
    def test_redirect_view_with_invalid_pk(self, rf):
        invalid_dataset_id = 999
        request = rf.get("study", kwargs={"pk": invalid_dataset_id})
        with pytest.raises(Http404):
            PublicationRedirectView.as_view()(request, id=invalid_dataset_id)


class TestPublicationDetailView:
    def test_detail_view_with_existing_names(self, client, publication):
        url = reverse(
            "publ:publication",
            kwargs={
                "study_name": publication.study.name,
                "publication_name": publication.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_detail_view_with_invalid_study_name(self, client, publication):
        url = reverse(
            "publ:publication",
            kwargs={
                "study_name": "invalid-study-name",
                "publication_name": publication.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
