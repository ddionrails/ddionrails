import json
import pprint

from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views.generic import DetailView

from ddionrails.helpers import RowHelper
from instruments.models import Question
from workspace.models import Basket

from .helpers import LabelTable
from .models import Dataset, Variable


def extend_context_for_variable(request, context):
    variable = context["variable"]
    study = variable.get_study()
    context["related_variables"] = variable.get_related_variables()
    context["label_table"] = LabelTable(context["related_variables"])
    context["questions"] = Question.objects.filter(
        questions_variables__variable=variable.id
    ) | Question.objects.filter(
        questions_variables__variable__target_variables__target_id=variable.id
    )
    context["study"] = study
    context["debug_string"] = pprint.pformat(variable.get_elastic(), width=120)
    context["concept"] = variable.get_concept()
    context["row_helper"] = RowHelper()
    context["basket_list"] = (
        Basket.objects.filter(study_id=study.id).filter(user_id=request.user.id).all()
    )  # TODO user!
    return context


def variable_redirect(request, id):
    variable = get_object_or_404(Variable, id=id)
    return redirect(str(variable))


def dataset_redirect(request, id):
    dataset = get_object_or_404(Dataset, id=id)
    return redirect(str(dataset))


class VariableDetailView(DetailView):
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
            name=self.kwargs["variable_name"],
            dataset__name=self.kwargs["dataset_name"],
            dataset__study__name=self.kwargs["study_name"],
        )
        return queryset.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variable = context["variable"]
        study = variable.get_study()
        context["study"] = study
        context["related_variables"] = variable.get_related_variables()
        context["label_table"] = LabelTable(context["related_variables"])
        context["questions"] = Question.objects.filter(
            questions_variables__variable=variable
        )
        context["debug_string"] = pprint.pformat(variable.get_elastic(), width=120)
        context["concept"] = variable.get_concept()
        context["row_helper"] = RowHelper()
        context["basket_list"] = (
            Basket.objects.filter(study_id=study.id)
            .filter(user_id=self.request.user.id)
            .all()
        )  # TODO user!
        return context


def variable_detail(request, study_name, dataset_name, variable_name):
    variable = (
        Variable.objects.filter(dataset__name=dataset_name)
        .filter(dataset__study__name=study_name)
        .filter(name=variable_name)
        .first()
    )
    context = extend_context_for_variable(request, dict(variable=variable))
    return render(request, "data/variable_detail.html", context=context)


def variable_json(request, study_name, dataset_name, variable_name):
    variable = (
        Variable.objects.filter(dataset__study__name=study_name)
        .filter(dataset__name=dataset_name)
        .get(name=variable_name)
    )
    var_json = variable.get_source(as_json=True)
    # TODO: use JsonResponse here
    return HttpResponse(var_json, content_type="application/json")


def dataset_detail(request, study_name, dataset_name):
    dataset = get_object_or_404(Dataset, study__name=study_name, name=dataset_name)
    context = dict(
        dataset=dataset, variables=dataset.variables.all(), study=dataset.study
    )
    return render(request, "data/dataset_detail.html", context=context)


def variable_preview_id(request, variable_id):
    variable = get_object_or_404(Variable, pk=variable_id)
    context = extend_context_for_variable(request, dict(variable=variable))
    response = dict(
        name=variable.name,
        title=variable.title(),
        type="variable",
        html=render(
            request, "data/variable_preview.html", context=context
        ).content.decode("utf8"),
    )
    return HttpResponse(json.dumps(response), content_type="text/plain")
