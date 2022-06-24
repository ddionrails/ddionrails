# -*- coding: utf-8 -*-

""" Views for ddionrails.data app """

from copy import deepcopy
from re import sub

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, RedirectView, TemplateView

from config.helpers import RowHelper
from ddionrails.instruments.models import Question
from ddionrails.workspace.models import Basket, BasketVariable

from .helpers import LabelTable
from .models import Dataset, Variable

NAMESPACE = "datasets"


class AllStudyDatasetsView(TemplateView):  # pylint: disable=too-many-ancestors
    """Table with all datasets of a study."""

    template_name = "data/study_datasets.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: data vs datasets; data should probably switched to datasets everywhere.
        context["namespace"] = NAMESPACE
        context["study"] = kwargs["study"]
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
            Dataset,
            study=self.kwargs["study"],
            name=self.kwargs["dataset_name"],
        )
        return dataset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = self.object.study
        context["variables"] = self.object.variables.all()
        context["namespace"] = NAMESPACE
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
        variable = Variable.objects.select_related(
            "dataset",
            "dataset__study",
            "dataset__conceptual_dataset",
            "dataset__analysis_unit",
            "concept",
            "period",
        ).get(
            dataset__study=self.kwargs["study"],
            dataset__name=self.kwargs["dataset_name"],
            name=self.kwargs["variable_name"],
        )
        return variable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study = self.object.get_study()
        context["study"] = study
        context["related_variables"] = self.object.get_related_variables()
        context["label_table"] = LabelTable(context["related_variables"])
        context["questions"] = Question.objects.filter(
            questions_variables__variable=self.object.id
        ).select_related("period", "instrument") | Question.objects.filter(
            questions_variables__variable__target_variables__target_id=self.object.id
        ).select_related(
            "period", "instrument"
        )
        context["questions"] = sorted(
            context["questions"], key=lambda question: question.period.label, reverse=True
        )
        # All questions are intended to be displayed separately in a bootstrap modal.
        # The subset here is to be displayed directly on the page.
        context["questions_subset"] = context["questions"][:5]
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
        variable_data = self._sort_variable_data(self.object.content_dict)
        context["variable_baskets_context"] = {
            "variable": {
                "id": str(context["variable"].id),
                "name": context["variable"].name,
                "data": variable_data,
            },
            "baskets": {
                basket.name: {
                    "basket_variable": getattr(
                        BasketVariable.objects.filter(
                            variable=context["variable"], basket=basket
                        ).first(),
                        "id",
                        "",
                    ),
                    "id": basket.id,
                }
                for basket in context["basket_list"]
            },
        }
        for measure in ordering:
            if measure in self.object.statistics:
                context["statistics"][measure] = self.object.statistics[measure]
        context["origin_variables"] = self.object.origin_variables_dict
        context["target_variables"] = self.object.target_variables_dict
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
