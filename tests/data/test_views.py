import json


import pytest

from django.http.response import Http404
from django.urls import reverse

from data.models import Variable
from data.views import (
    RowHelper,
    # dataset_detail,
    dataset_redirect,
    # extend_context_for_variable,
    # variable_detail,
    # variable_json,
    # variable_preview_id,
    variable_redirect,
)

pytestmark = [pytest.mark.data, pytest.mark.views]


class TestRowHelper:
    def test_row_method(self):
        row_helper = RowHelper()
        assert row_helper.row() is False

    def test_row_method_true(self):
        """ Everytime row is called, i is incremented.
            If it hits 4, it returns True
        """
        row_helper = RowHelper()
        row_helper.i = 3
        assert row_helper.row() == True

    def test_reset_method(self):
        row_helper = RowHelper()
        row_helper.i = 1
        row_helper.reset()
        assert row_helper.i == 0


class TestExtendContextForVariable:
    pass


class TestDatasetDetailView:
    def test_detail_view_with_existing_names(self, client, dataset):
        url = reverse(
            "data:dataset",
            kwargs={"study_name": dataset.study.name, "dataset_name": dataset.name},
        )
        response = client.get(url)
        assert response.status_code == 200
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

        # TODO view returns HttpResponseNotFound instead of raising Http404
        response = client.get(url)
        assert response.status_code == 404

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
        response = dataset_redirect(request, id=dataset.pk)
        assert response.status_code == 302

    def test_redirect_view_with_invalid_pk(self, rf, dataset):
        invalid_dataset_id = 999
        request = rf.get("study", kwargs={"pk": invalid_dataset_id})
        with pytest.raises(Http404):
            dataset_redirect(request, id=invalid_dataset_id)


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
        assert response.status_code == 200
        template = "data/variable_detail.html"
        assert template in (t.name for t in response.templates)

        # TODO : Test context. uses extend_context_for_variable()


class TestVariableJsonView:
    def test_json_view_with_existing_names(self, client, mocker, variable):
        url = reverse(
            "data:variable_json",
            kwargs={
                "study_name": variable.dataset.study.name,
                "dataset_name": variable.dataset.name,
                "variable_name": variable.name,
            },
        )
        mocked_get_source = mocker.patch.object(Variable, "get_source")
        mocked_get_source.return_value = dict(
            study=variable.dataset.study.name,
            dataset=variable.dataset.name,
            variable=variable.name,
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

        # content = json.loads(response.content)
        #
        # assert content['study'] == variable.dataset.study.name
        # assert content['dataset'] == variable.dataset.name
        # assert content['variable'] == variable.name

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
        assert response.status_code == 200
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
        assert response.status_code == 404


class TestVariableRedirectView:
    def test_redirect_view_with_valid_pk(self, rf, variable):
        request = rf.get("variable", kwargs={"pk": variable.pk})
        response = variable_redirect(request, id=variable.pk)
        assert response.status_code == 302

    def test_redirect_view_with_invalid_pk(self, db, rf):
        invalid_pk = 999
        request = rf.get("variable", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            variable_redirect(request, id=invalid_pk)
