# -*- coding: utf-8 -*-

""" Views for ddionrails.data app """

import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, RedirectView

from config.helpers import RowHelper
from ddionrails.instruments.models import Question
from ddionrails.workspace.models import Basket

from .helpers import LabelTable
from .models import Dataset, Variable


class DatasetDetailView(DetailView):
    """ Dataset detail view
        ---

        the view expects two arguments:
            - study_name (str)
            - dataset_name (str)

        the view returns a context dictionary including:
            - the dataset object (Dataset)
            - the related study object (Study)
            - all related variable objects (Queryset Variable)
    """

    model = Dataset
    template_name = "data/dataset_detail.html"

    def get_object(self, queryset=None):
        dataset = get_object_or_404(
            Dataset,
            study__name=self.kwargs["study_name"],
            name=self.kwargs["dataset_name"],
        )
        return dataset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = self.object.study
        context["variables"] = self.object.variables.all()
        return context


class VariableRedirectView(RedirectView):
    """ The Variable redirect view redirects
        from
        /variable/<int:id>
        to
        /<str:study_name>/data/<str:dataset_name>/<str:variable_name>
    """

    def get_redirect_url(self, *args, **kwargs):
        variable = get_object_or_404(Variable, id=kwargs["id"])
        return variable.get_absolute_url()


class VariableDetailView(DetailView):
    """ Variable detail view
        ---

        the view expects three arguments:
            - study_name (str)
            - dataset_name (str)
            - variable_name (str)

        the view returns a context dictionary including:
            - the variable object (Dataset)
            - the related dataset object (Study)
            - the related study object (Study)
            - all related variable objects (Queryset Variable)
    """

    model = Variable
    template_name = "data/variable_detail.html"

    def get_object(self, queryset=None):
        queryset = Variable.objects.select_related(
            "dataset",
            "dataset__study",
            "dataset__conceptual_dataset",
            "dataset__analysis_unit",
            "concept",
            "period",
        ).filter(
            dataset__study__name=self.kwargs["study_name"],
            dataset__name=self.kwargs["dataset_name"],
            name=self.kwargs["variable_name"],
        )
        return queryset.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study = self.object.get_study()
        context["study"] = study
        context["related_variables"] = self.object.get_related_variables()
        context["label_table"] = LabelTable(context["related_variables"])
        context["questions"] = Question.objects.filter(
            questions_variables__variable=self.object.id
        ) | Question.objects.filter(
            questions_variables__variable__target_variables__target_id=self.object.id
        )
        context["concept"] = self.object.get_concept()
        context["row_helper"] = RowHelper()
        context["basket_list"] = (
            Basket.objects.filter(study_id=study.id)
            .filter(user_id=self.request.user.id)
            .all()
        )  # TODO user!

        # Ordering of keys in statistics dictionary
        context["statistics"] = dict()
        ORDERING = (
            "Min.",
            "1st Qu.",
            "Median",
            "Mean",
            "3rd Qu.",
            "Max.",
            "valid",
            "invalid",
        )
        for measure in ORDERING:
            if measure in self.object.statistics:
                context["statistics"][measure] = self.object.statistics[measure]
        return context


# request is a required parameter
def variable_json(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    dataset_name: str,
    variable_name: str,
):
    variable = get_object_or_404(
        Variable,
        dataset__study__name=study_name,
        dataset__name=dataset_name,
        name=variable_name,
    )
    return JsonResponse(variable.to_dict())
