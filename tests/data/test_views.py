# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.data app """

import pytest
from django.http.response import Http404
from django.urls import reverse

from ddionrails.data.views import VariableRedirectView
from ddionrails.studies.models import Study
from tests import status

pytestmark = [pytest.mark.data, pytest.mark.views]


class TestDatasetDetailView:
    def test_detail_view_with_existing_names(self, client, dataset):
        url = reverse(
            "data:dataset_detail",
            kwargs={"study": dataset.study, "dataset_name": dataset.name},
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/dataset_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["dataset"] == dataset
        assert response.context["study"] == dataset.study
        expected_variables = list(dataset.variables.all())
        output_variables = list(response.context["variables"])
        assert expected_variables == output_variables

    def test_detail_view_with_invalid_study_name(self, client, dataset):
        url = reverse(
            "data:dataset_detail",
            kwargs={"study": Study.objects.none(), "dataset_name": dataset.name},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_dataset_name(self, client, dataset):
        invalid_dataset_name = "invalid-dataset-name"
        url = reverse(
            "data:dataset_detail",
            kwargs={
                "study": dataset.study,
                "dataset_name": invalid_dataset_name,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestVariableDetailView:
    def test_detail_view_with_existing_names(self, client, variable):
        url = reverse(
            "data:variable_detail",
            kwargs={
                "study": variable.dataset.study,
                "dataset_name": variable.dataset.name,
                "variable_name": variable.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/variable_detail.html"
        assert template in (t.name for t in response.templates)


class TestVariableRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, variable):
        request = rf.get("variable", kwargs={"pk": variable.pk})
        response = VariableRedirectView.as_view()(request, id=variable.pk)
        assert status.HTTP_302_FOUND == response.status_code

    @pytest.mark.django_db
    def test_redirect_view_with_invalid_pk(self, rf):
        invalid_pk = 999
        request = rf.get("variable", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            VariableRedirectView.as_view()(request, id=invalid_pk)
