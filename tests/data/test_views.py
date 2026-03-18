# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.data app"""

import pytest
from django.http.response import Http404
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from ddionrails.data.views import VariableRedirectView
from ddionrails.studies.models import Study
from tests import status
from tests.model_factories import DatasetFactory, VariableFactory

pytestmark = [pytest.mark.data, pytest.mark.views]


class TestDatasetDetailView(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client()
        cls.dataset = DatasetFactory()
        return super().setUpClass()

    def test_detail_view_with_existing_names(self):
        url = reverse(
            "data:dataset_detail",
            kwargs={"study": self.dataset.study, "dataset_name": self.dataset.name},
        )
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/dataset_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["dataset"] == self.dataset
        assert response.context["study"] == self.dataset.study
        expected_variables = list(self.dataset.variables.all())
        output_variables = list(response.context["variables"])
        assert expected_variables == output_variables

    def test_detail_view_with_invalid_study_name(self):
        url = reverse(
            "data:dataset_detail",
            kwargs={"study": Study.objects.none(), "dataset_name": self.dataset.name},
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_dataset_name(self):
        invalid_dataset_name = "invalid-dataset-name"
        url = reverse(
            "data:dataset_detail",
            kwargs={
                "study": self.dataset.study,
                "dataset_name": invalid_dataset_name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestVariableDetailView(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client()
        cls.variable = VariableFactory()
        return super().setUpClass()

    def test_detail_view_with_existing_names(self):
        url = reverse(
            "data:variable_detail",
            kwargs={
                "study": self.variable.dataset.study,
                "dataset_name": self.variable.dataset.name,
                "variable_name": self.variable.name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "data/variable_detail.html"
        assert template in (t.name for t in response.templates)


class TestVariableRedirectView(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.rf = RequestFactory()
        cls.variable = VariableFactory()
        return super().setUpClass()

    def test_redirect_view_with_valid_pk(self):
        request = self.rf.get("variable", kwargs={"pk": self.variable.pk})
        response = VariableRedirectView.as_view()(request, id=self.variable.pk)
        assert status.HTTP_302_FOUND == response.status_code

    def test_redirect_view_with_invalid_pk(self):
        invalid_pk = 999
        request = self.rf.get("variable", kwargs={"pk": invalid_pk})
        with pytest.raises(Http404):
            VariableRedirectView.as_view()(request, id=invalid_pk)
