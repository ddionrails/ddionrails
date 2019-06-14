# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for views in ddionrails.data app """

import json

import pytest
from django.http.response import Http404
from django.urls import reverse

from ddionrails.data.models import Variable
from ddionrails.data.views import DatasetRedirectView, RowHelper, VariableRedirectView

from tests import status

pytestmark = [pytest.mark.data, pytest.mark.views]


class TestRowHelper:
    def test_row_method(self):
        row_helper = RowHelper()
        assert row_helper.row() is False

    def test_row_method_true(self):
        """ Everytime row is called, row_index is incremented.
            If it hits 4, it returns True
        """
        row_helper = RowHelper()
        row_helper.row_index = 3
        assert row_helper.row() == True

    def test_reset_method(self):
        row_helper = RowHelper()
        row_helper.row_index = 1
        row_helper.reset()
        assert row_helper.row_index == 0


class TestDatasetDetailView:
    def test_detail_view_with_existing_names(self, client, dataset):
        url = reverse(
            "data:dataset",
            kwargs={"study_name": dataset.study.name, "dataset_name": dataset.name},
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
        invalid_study_name = "invalid-study-name"
        url = reverse(
            "data:dataset",
            kwargs={"study_name": invalid_study_name, "dataset_name": dataset.name},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_dataset_name(self, client, dataset):
        invalid_dataset_name = "invalid-dataset-name"
        url = reverse(
            "data:dataset",
            kwargs={
                "study_name": dataset.study.name,
                "dataset_name": invalid_dataset_name,
            },
        )

        # TODO view returns HttpResponseNotFound instead of raising Http404
        response = client.get(url)
        assert response.status_code == 404


class TestDatasetRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, dataset):
        request = rf.get("dataset", kwargs={"pk": dataset.pk})
        response = DatasetRedirectView.as_view()(request, id=dataset.pk)
        assert status.HTTP_302_FOUND == response.status_code

    def test_redirect_view_with_invalid_pk(self, rf, dataset):
        invalid_dataset_id = 999
        request = rf.get("study", kwargs={"pk": invalid_dataset_id})
        with pytest.raises(Http404):
            DatasetRedirectView.as_view()(request, id=invalid_dataset_id)


class TestVariableDetailView:
    def test_detail_view_with_existing_names(self, client, mocker, variable):
        url = reverse(
            "data:variable",
            kwargs={
                "study_name": variable.dataset.study.name,
                "dataset_name": variable.dataset.name,
                "variable_name": variable.name,
            },
        )
        mocked_get_source = mocker.patch.object(Variable, "get_source")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/variable_detail.html"
        assert template in (t.name for t in response.templates)


class TestVariableJsonView:
    def test_json_view_with_existing_names(self, client, variable):
        url = reverse(
            "data:variable_json",
            kwargs={
                "study_name": variable.dataset.study.name,
                "dataset_name": variable.dataset.name,
                "variable_name": variable.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        assert response["Content-Type"] == "application/json"
        content = response.json()
        assert content['name'] == variable.name
        assert content['scale'] == variable.scale
        assert content['uni'] == variable.categories


    # TODO non existing study => 404
    def test_json_view_with_invalid_study_name(self, client, mocker, variable):
        pass

    # TODO non existing dataset => 404
    def test_json_view_with_invalid_dataset_name(self, client, mocker, variable):
        pass

    # TODO non existing variable => 404
    def test_json_view_with_invalid_variable_name(self, client, mocker, variable):
        pass


class TestVariablePreviewIdView:
    def test_preview_id_view_with_valid_pk(self, client, mocker, variable):
        url = reverse("api:variable_preview", kwargs={"variable_id": variable.pk})
        mocked_get_source = mocker.patch.object(Variable, "get_source")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/variable_preview.html"
        assert template in (t.name for t in response.templates)
        assert response["Content-Type"] == "text/plain"

        content = json.loads(response.content)
        assert content["name"] == variable.name
        assert content["title"] == variable.title()
        assert content["type"] == "variable"

        # TODO test html content
        assert variable.name in content["html"]

    def test_preview_id_view_with_invalid_pk(self, client, db):
        invalid_pk = 999
        url = reverse("api:variable_preview", kwargs={"variable_id": invalid_pk})

        # TODO view returns HttpResponseNotFound instead of raising Http404
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestVariableRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, variable):
        request = rf.get("variable", kwargs={"pk": variable.pk})
        response = VariableRedirectView.as_view()(request, id=variable.pk)
        assert status.HTTP_302_FOUND == response.status_code

    def test_redirect_view_with_invalid_pk(self, db, rf):
        invalid_pk = 999
        request = rf.get("variable", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            VariableRedirectView.as_view()(request, id=invalid_pk)
