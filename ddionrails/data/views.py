# -*- coding: utf-8 -*-

"""Views for ddionrails.data app"""

from copy import deepcopy
from re import sub
from typing import List

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, RedirectView, TemplateView

from config.helpers import RowHelper
from ddionrails.instruments.models import QuestionItem
from ddionrails.studies.models import Study
from ddionrails.studies.views import get_study_context
from ddionrails.workspace.models import Basket, BasketVariable

from .models import Dataset, Variable

NAMESPACE = "datasets"


class AllStudyDatasetsView(TemplateView):  # pylint: disable=too-many-ancestors
    """Table with all datasets of a study."""

    template_name = "data/study_datasets.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["namespace"] = NAMESPACE
        context["study"] = kwargs["study"]
        context = context | get_study_context(Study.objects.get(name=kwargs["study"]))
        return context


class DatasetDetailView(DetailView):
    """Dataset detail view
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
            Dataset.objects.select_related(
                "period", "analysis_unit", "conceptual_dataset"
            ),
            study=self.kwargs["study"],
            name=self.kwargs["dataset_name"],
        )
        return dataset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = self.object.study
        context["variables"] = self.object.variables.all()
        context["namespace"] = NAMESPACE
        context = context | get_study_context(self.object.study)
        return context


class VariableRedirectView(RedirectView):
    """The Variable redirect view redirects
    from
    /variable/<int:id>
    to
    /<str:study_name>/data/<str:dataset_name>/<str:variable_name>
    """

    def get_redirect_url(self, *args, **kwargs):
        variable = get_object_or_404(Variable, id=kwargs["id"])
        return variable.get_absolute_url()


class DataRedirectView(RedirectView):
    """RedirectView for instruments.Question model"""

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        uri = self.request.build_absolute_uri()
        uri = sub("/data/", "/datasets/", uri)
        return uri


class DatasetRedirectView(RedirectView):
    """Redirect from uuid to full path url of a dataset."""

    def get_redirect_url(self, *args, **kwargs):
        dataset = get_object_or_404(Dataset, id=kwargs["id"])
        return dataset.get_absolute_url()


class VariableDetailView(DetailView):
    """Variable detail view
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
        variable = (
            Variable.objects.select_related(
                "dataset",
                "dataset__study",
                "dataset__conceptual_dataset",
                "dataset__analysis_unit",
                "concept",
                "period",
            )
            .prefetch_related("dataset__attachments")
            .get(
                dataset__study=self.kwargs["study"],
                dataset__name=self.kwargs["dataset_name"],
                name=self.kwargs["variable_name"],
            )
        )
        return variable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study = self.object.get_study()
        variable: Variable = self.object
        context["study"] = study
        context["related_variables"] = self.object.get_related_variables()
        if variable.period.name == "0":
            context["items"] = _get_related_long_items(self.object)
        else:
            context["items"] = _get_related_items(self.object)
        # All questions are intended to be displayed separately in a bootstrap modal.
        # The subset here is to be displayed directly on the page.
        context["items_subset"] = context["items"][:5]
        context["concept"] = self.object.get_concept()
        context["row_helper"] = RowHelper()
        context["basket_list"] = (
            Basket.objects.filter(study_id=study.id)
            .filter(user_id=self.request.user.id)
            .all()
        )

        # Ordering of keys in statistics dictionary
        context["statistics"] = {}
        ordering = (
            "Min.",
            "1st Qu.",
            "Median",
            "Mean",
            "3rd Qu.",
            "Max.",
            "valid",
            "invalid",
        )
        variable_data = self._sort_variable_data(variable.content_dict)
        context["variable_baskets_context"] = {
            "variable": {
                "id": context["variable"].id,
                "name": context["variable"].name,
                "data": variable_data,
            },
            "baskets": [
                {
                    "name": basket.name,
                    "variableIsInBasket": BasketVariable.objects.filter(
                        variable=context["variable"], basket=basket
                    ).exists(),
                    "id": basket.id,
                }
                for basket in context["basket_list"]
            ],
        }
        for measure in ordering:
            if measure in variable.statistics:
                context["statistics"][measure] = variable.statistics[measure]
        context["origin_variables"] = variable.origin_variables_dict
        context["target_variables"] = variable.target_variables_dict
        context["origin_variables_exist"] = bool(variable.origin_variables.count())
        context["target_variables_exist"] = bool(variable.target_variables.count())
        context["related_variables_exist"] = bool(variable.get_related_variables())
        context = context | get_study_context(study)
        return context

    @staticmethod
    def _sort_variable_data(data):
        _data = deepcopy(data)
        try:
            statistics = _data["uni"]
            sorting_list = zip(
                statistics["values"],
                statistics["labels"],
                statistics["missings"],
                statistics["frequencies"],
            )
        except KeyError:
            return _data
        positive = []
        negative = []
        for package in sorting_list:
            if int(package[0]) >= 0:
                positive.append(package)
            else:
                negative.append(package)

        sorted_list = sorted(negative, key=lambda item: item[0])
        sorted_list += sorted(positive, key=lambda item: item[0], reverse=True)
        del sorting_list, positive, negative
        for index, package in enumerate(sorted_list):
            statistics["values"][index] = package[0]
            statistics["labels"][index] = package[1]
            statistics["missings"][index] = package[2]
            statistics["frequencies"][index] = package[3]

        _data["uni"] = statistics

        return _data


def _get_related_long_items(variable: Variable) -> List[QuestionItem]:
    return list(
        QuestionItem.objects.filter(
            variables__variable__id=variable.id,
        ).select_related("question", "question__period", "question__instrument")
    )


def _get_related_items(variable: Variable) -> List[QuestionItem]:
    return list(
        QuestionItem.objects.filter(
            question__instrument__period=variable.period,
            variables__variable__id=variable.id,
        )
        .select_related("question", "question__period", "question__instrument")
        .order_by("-question__period__name")
        .distinct()
    )
