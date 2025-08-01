# -*- coding: utf-8 -*-

"""Views for ddionrails.workspace app"""

import uuid
from collections import OrderedDict
from urllib.parse import urlencode

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.forms.widgets import HiddenInput
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse

from ddionrails.concepts.models import Concept
from ddionrails.data.models import Variable
from ddionrails.workspace.forms import BasketForm
from ddionrails.workspace.models import Basket, BasketVariable

from .decorator import own_basket_only


# request is a required parameter
def basket_list(request: WSGIRequest):  # pylint: disable=unused-argument
    """ListView for workspace.Basket model"""
    if request.user.is_authenticated:
        _basket_list = request.user.baskets.all()
    else:
        _basket_list = []
    context = {"basket_list": _basket_list}
    return render(request, "workspace/basket_list.html", context=context)


NOTE = (
    "The script-generators help you especially to merge variables from "
    "different year-specific datasets (e.g. bhp, bgp) to one wide file."
    "This (and more) work is already done in the long files (e.g. pl, hl),"
    " which you find in the top-level directory."
    "If you still want to use the script-generator, please note that only the files"
    ' in the "raw" subdirectory can be processed.'
    'Please specify the complete address of the "raw" subdirectory'
    ' (e.g. D:\\v35\\raw) as your "Input path".'
)


# request is a required parameter
@own_basket_only
def basket_detail(
    request: WSGIRequest, basket_id: int  # pylint: disable=unused-argument
):
    """DetailView for workspace.Basket model"""
    basket = get_object_or_404(Basket, pk=basket_id)
    variable_list = basket.variables.all()
    vars_with_concept, vars_without_concept = [], []
    for variable in variable_list:
        if variable.concept:
            vars_with_concept.append(variable)
        else:
            vars_without_concept.append(variable)
    concept_list = sorted(
        Concept.objects.filter(
            id__in={variable.concept.id for variable in vars_with_concept}
        ).all(),
        key=lambda x: x.name,
    )
    related_variable_list = (
        Variable.objects.filter(concept_id__in={concept.id for concept in concept_list})
        .filter(dataset__study_id=basket.study.id)
        .prefetch_related("dataset", "dataset__period", "period", "concept")
        .all()
    )
    period_list = []
    for variable in related_variable_list:
        try:
            period_list.append(variable.dataset.period.name)
        # afuetterer: there might be no period?
        except AttributeError:
            period_list.append("")
    period_list = sorted(set(period_list))
    related_variable_table = OrderedDict()
    for concept in concept_list:
        related_variable_table[concept.name] = OrderedDict(
            id=concept.id,
            label=concept.label,
            periods=OrderedDict([(period, []) for period in period_list]),
        )
    bad_variables = []
    for variable in related_variable_list:
        try:
            period_name = variable.dataset.period.name
        # afuetterer: there might be no period?
        except AttributeError:
            period_name = ""
        try:
            related_variable_table[variable.concept.name]["periods"][period_name].append(
                {
                    "name": variable.name,
                    "link": variable.get_direct_url(),
                    "active": variable in variable_list,
                    "id": variable.id,
                }
            )
            if related_variable_table[variable.concept.name]["label"] == "":
                related_variable_table[variable.concept.name]["label"] = variable.label
        except (KeyError, ValueError):
            bad_variables.append(variable)

    context = {
        "basket": basket,
        "study": basket.study,
        "variable_list": variable_list,
        "vars_with_concept": vars_with_concept,
        "vars_without_concept": vars_without_concept,
        "has_vars_without_concept": len(vars_without_concept) > 0,
        "related_variable_table": related_variable_table,
        "period_list": period_list,
        "concept_list": concept_list,
        "note": None,
    }

    # Add note about Script generator
    # see: https://github.com/ddionrails/ddionrails/issues/359
    if basket.study.name == "soep-core":
        context["note"] = NOTE

    return render(request, "workspace/basket_detail.html", context=context)


# request is a required parameter
def basket_new(request: WSGIRequest):  # pylint: disable=unused-argument
    """CreateView for a new Basket"""
    query = request.GET.dict()
    if query is None:
        query = request.POST.dict()
    _next = query.get("next")
    if request.method == "POST":
        form = BasketForm(request.POST)
        form.fields["user"].widget = HiddenInput()
        if form.is_valid():
            basket = form.save(commit=False)
            basket.user = request.user
            basket.save()
            messages.info(request, "Basket successfully created.")
            if _next is not None:
                return redirect(_next)
            return redirect(reverse("workspace:basket_list"))
    else:
        form = BasketForm(initial={"user": request.user.id})
        form.fields["user"].widget = HiddenInput()
    context: dict[str, str | BasketForm] = {"form": form}
    context["next"] = query.get("next", reverse("workspace:basket_list"))
    return render(request, "workspace/basket_create.html", context=context)


# request is a required parameter
@own_basket_only
def basket_search(
    request: WSGIRequest, basket_id: int  # pylint: disable=unused-argument
):
    """Search view in the context of a basket's study"""
    basket = get_object_or_404(Basket, pk=basket_id)
    # e.g. Studies=["soep-is"]
    query_string = urlencode({"Study": f'["{basket.study.title()}"]'})
    # e.g. http://localhost/search/variables?Study=["soep-is"]
    url = f"/search/variables?{query_string}"
    return redirect(url)


# request is a required parameter
@own_basket_only
def basket_delete(
    request: WSGIRequest, basket_id: int  # pylint: disable=unused-argument
) -> HttpResponseRedirect:
    """Delete view for workspace.Basket model"""
    basket = get_object_or_404(Basket, pk=basket_id)
    basket.delete()
    return redirect(reverse("workspace:basket_list"))


# request is a required parameter
@own_basket_only
def add_concept(
    request: WSGIRequest,  # pylint: disable=unused-argument
    basket_id: int,
    concept_id: uuid.UUID,
) -> HttpResponseRedirect:
    """Add variables to a basket by a given concept id"""
    basket = get_object_or_404(Basket, pk=basket_id)
    study_id = basket.study_id
    variable_list = (
        Variable.objects.filter(dataset__study_id=study_id)
        .filter(concept_id=concept_id)
        .all()
    )
    for variable in variable_list:
        try:
            BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except (IntegrityError, ValueError, TypeError):
            continue
    return redirect(request.META.get("HTTP_REFERER"))


# request is a required parameter
@own_basket_only
def remove_concept(
    request: WSGIRequest,  # pylint: disable=unused-argument
    basket_id: int,
    concept_id: uuid.UUID,
) -> HttpResponseRedirect:
    """Remove variables from a basket by a given concept id"""

    _ = get_object_or_404(Concept, id=concept_id)
    BasketVariable.objects.filter(
        variable__concept_id=concept_id, basket_id=basket_id
    ).delete()
    return redirect(request.META.get("HTTP_REFERER"))


# request is a required parameter
@own_basket_only
def basket_to_csv(
    request: WSGIRequest, basket_id: int  # pylint: disable=unused-argument
) -> HttpResponse:
    """Export a basket to CSV"""
    basket = get_object_or_404(Basket, pk=basket_id)
    csv = basket.to_csv()
    response = HttpResponse(csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="basket.csv"'
    return response
