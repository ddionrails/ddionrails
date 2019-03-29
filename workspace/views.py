import json
import pprint
from collections import OrderedDict

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.forms.widgets import HiddenInput
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from concepts.models import Concept
from data.models import Variable

from .forms import BasketForm, UserCreationForm
from .models import Basket, BasketVariable, Script
from .scripts import SoepStata


def own_basket_only(view):
    """Decorator for basket-related views."""

    def wrapper(request: WSGIRequest, basket_id: int, *args, **kwargs):
        basket = get_object_or_404(Basket, pk=basket_id)
        if basket.user == request.user:
            return view(request, basket_id, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper


# ---------------------------------------------------------


def account_overview(request: WSGIRequest):
    if request.user.is_authenticated:
        context = dict(user=request.user)
        return render(request, "workspace/account.html", context=context)
    else:
        return HttpResponse("Unauthorized", status=401)


def basket_list(request: WSGIRequest):
    if request.user.is_authenticated:
        basket_list = request.user.baskets.all()
    else:
        basket_list = []
    context = dict(basket_list=basket_list)
    return render(request, "workspace/basket_list.html", context=context)


@own_basket_only
def render_script(request, basket_id, script_name):
    basket = get_object_or_404(Basket, pk=basket_id)
    context = dict(
        basket=basket, variables=basket.variables.all(), script_name=script_name
    )
    template = "scripts/%s.html" % script_name
    return render(request, template, context=context)


@own_basket_only
def add_variable(request: WSGIRequest, basket_id: int, variable_id: int):
    try:
        basket_variable = BasketVariable(basket_id=basket_id, variable_id=variable_id)
        basket_variable.clean()
        basket_variable.save()
    except:
        pass
    return redirect(request.META.get("HTTP_REFERER"))


@own_basket_only
def remove_variable(request: WSGIRequest, basket_id: int, variable_id: int):
    try:
        relation = get_object_or_404(
            BasketVariable, basket_id=basket_id, variable_id=variable_id
        )
        relation.delete()
    except:
        pass
    return redirect(request.META.get("HTTP_REFERER"))


@own_basket_only
def add_concept(request: WSGIRequest, basket_id: int, concept_id: int):
    basket = get_object_or_404(Basket, pk=basket_id)
    study_id = basket.study_id
    variable_list = (
        Variable.objects.filter(dataset__study_id=study_id)
        .filter(concept_id=concept_id)
        .all()
    )
    for variable in variable_list:
        try:
            relation, status = BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except:
            pass
    return redirect(request.META.get("HTTP_REFERER"))


@own_basket_only
def remove_concept(request, basket_id, concept_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    study_id = basket.study_id
    variable_list = (
        Variable.objects.filter(dataset__study_id=study_id)
        .filter(concept_id=concept_id)
        .all()
    )
    for variable in variable_list:
        try:
            relation = get_object_or_404(
                BasketVariable, basket_id=basket_id, variable_id=variable.id
            )
            relation.delete()
        except BasketVariable.DoesNotExist:
            pass
    return redirect(request.META.get("HTTP_REFERER"))


@own_basket_only
def basket_to_csv(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    csv = basket.to_csv()
    response = HttpResponse(csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="basket.csv"'
    return response


note = (
    "The script-generators help you especially to merge variables from "
    "different year-specific datasets (e.g. bhp, bgp) to one wide file."
    "This (and more) work is already done in the long files (e.g. pl, hl),"
    " which you find in the top-level directory."
    "If you still want to use the script-generator, please note that only the files"
    ' in the "raw" subdirectory can be processed.'
    'Please specify the complete adress of the "raw" subdirectory'
    ' (e.g. D:\\v35\\raw) as your "Input path".'
)


@own_basket_only
def basket_detail(request: WSGIRequest, basket_id: int):
    basket = get_object_or_404(Basket, pk=basket_id)
    variable_list = basket.variables.all()
    vars_with_concept, vars_without_concept = list(), list()
    for variable in variable_list:
        if variable.concept:
            vars_with_concept.append(variable)
        else:
            vars_without_concept.append(variable)
    concept_list = sorted(
        Concept.objects.filter(
            id__in=set([v.concept.id for v in vars_with_concept])
        ).all(),
        key=lambda x: x.name,
    )
    related_variable_list = (
        Variable.objects.filter(
            concept_id__in=set([concept.id for concept in concept_list])
        )
        .filter(dataset__study_id=basket.study.id)
        .prefetch_related("dataset", "dataset__period", "period", "concept")
        .all()
    )
    period_list = []
    for v in related_variable_list:
        try:
            period_list.append(v.dataset.period.name)
        except:
            period_list.append("")
    period_list = sorted(set(period_list))
    related_variable_table = OrderedDict()
    for concept in concept_list:
        related_variable_table[concept.name] = OrderedDict(
            id=concept.id,
            label=concept.label,
            periods=OrderedDict([(p, list()) for p in period_list]),
        )
    bad_variables = list()
    for v in related_variable_list:
        try:
            period_name = v.dataset.period.name
        except:
            period_name = ""
        try:
            related_variable_table[v.concept.name]["periods"][period_name].append(
                dict(name=v.name, link=str(v), active=v in variable_list, id=v.id)
            )
            if related_variable_table[v.concept.name]["label"] == "":
                related_variable_table[v.concept.name]["label"] = v.label
        except:
            bad_variables.append(v)

    context = dict(
        basket=basket,
        study=basket.study,
        variable_list=variable_list,
        vars_with_concept=vars_with_concept,
        vars_without_concept=vars_without_concept,
        has_vars_without_concept=len(vars_without_concept) > 0,
        related_variable_table=related_variable_table,
        period_list=period_list,
        concept_list=concept_list,
        debug_string=pprint.pformat(
            dict(
                table_input=related_variable_table,
                bad_variables=bad_variables,
                period_list=period_list,
            )
        ),
        note=None,
    )

    # Add note about Script generator
    # see: https://github.com/ddionrails/ddionrails/issues/359
    if basket.study.name == "soep-core":
        context["note"] = note

    return render(request, "workspace/basket_detail.html", context=context)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = UserCreationForm()
    context = dict(form=form)
    return render(request, "registration/register.html", context=context)


def basket_new(request):
    if request.method == "POST":
        form = BasketForm(request.POST)
        form.fields["user"].widget = HiddenInput()
        if form.is_valid():
            basket = form.save(commit=False)
            basket.user = request.user
            basket.save()
            messages.info(request, "Basket successfully created.")
            return redirect("/workspace/baskets/")
    else:
        form = BasketForm(initial=dict(user=request.user.id))
        form.fields["user"].widget = HiddenInput()
    context = dict(form=form)
    return render(request, "workspace/basket_create.html", context=context)


@own_basket_only
def script_detail(request, basket_id, script_id):
    script = get_object_or_404(Script, pk=script_id)
    if request.method == "POST":
        script.name = request.POST.get("field_name", "")
        script.label = request.POST.get("field_label", "")
        script.generator_name = request.POST.get("field_generator_name", "")
        settings_dict = {
            key.replace("settings_", ""): value
            for key, value in request.POST.items()
            if "settings_" in key
        }
        script.settings = json.dumps(settings_dict)
        script.save()
    else:
        settings_dict = json.loads(script.settings)
    script_config = script.get_config()
    fields = script_config.fields
    for field in fields:
        if field["name"] in settings_dict.keys():
            field["value"] = settings_dict[field["name"]]
        if "value" not in field.keys():
            field["value"] = script_config.DEFAULT_DICT[field["name"]]
    s = script.get_script_input()
    context = dict(
        basket=script.basket,
        script=script,
        fields=fields,
        settings=settings_dict,
        s=s,
        debug_string=pprint.pformat(s),
    )
    return render(request, "workspace/script_detail.html", context=context)


@own_basket_only
def basket_search(request: WSGIRequest, basket_id: int):
    basket = get_object_or_404(Basket, pk=basket_id)
    context = dict(basket=basket, study_id=basket.study_id)
    return render(request, "workspace/angular.html", context=context)


@own_basket_only
def script_raw(request: WSGIRequest, basket_id: int, script_id: int):
    script = get_object_or_404(Script, pk=script_id)
    text = script.get_script_input()["text"]
    return HttpResponse(text, content_type="text/plain")


@own_basket_only
def basket_delete(request: WSGIRequest, basket_id: int):
    basket = get_object_or_404(Basket, pk=basket_id)
    basket.delete()
    return redirect("/workspace/baskets/")


@own_basket_only
def script_delete(request: WSGIRequest, basket_id: int, script_id: int):
    script = get_object_or_404(Script, pk=script_id)
    script.delete()
    return redirect("/workspace/baskets/%s" % basket_id)


def user_delete(request: WSGIRequest):
    request.user.delete()
    return redirect("/workspace/logout/")


@own_basket_only
def script_new_lang(request: WSGIRequest, basket_id: int, generator_name: str):
    basket = get_object_or_404(Basket, pk=basket_id)
    script_count = basket.script_set.count() + 1
    script_name = f"script-{script_count}"
    script = Script.objects.create(
        name=script_name,
        basket_id=basket_id,
        settings=SoepStata.DEFAULT_CONFIG,
        generator_name=generator_name,
    )
    return redirect(script.get_absolute_url())


@own_basket_only
def script_new(request: WSGIRequest, basket_id: int):
    basket = get_object_or_404(Basket, pk=basket_id)
    script_count = basket.script_set.count() + 1
    script_name = f"script-{script_count}"
    script = Script.objects.create(
        name=script_name, basket_id=basket_id, settings=SoepStata.DEFAULT_CONFIG
    )
    return redirect(script.get_absolute_url())
