# -*- coding: utf-8 -*-

""" Views for ddionrails.workspace app: Script related views """

import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from ddionrails.workspace.models import Basket, Script
from ddionrails.workspace.scripts import SoepStata

from .decorator import own_basket_only


# request is a required parameter
@own_basket_only
def render_script(request, basket_id, script_name):  # pylint: disable=unused-argument
    basket = get_object_or_404(Basket, pk=basket_id)
    context = dict(
        basket=basket, variables=basket.variables.all(), script_name=script_name
    )
    template = "scripts/%s.html" % script_name
    return render(request, template, context=context)


# request is a required parameter
@own_basket_only
def script_detail(
    request: WSGIRequest, basket_id: int, script_id: int
):  # pylint: disable=unused-argument
    """ DetailView for workspace.Script model """
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
    script_input = script.get_script_input()
    context = dict(
        basket=script.basket,
        script=script,
        fields=fields,
        settings=settings_dict,
        s=script_input,
    )
    return render(request, "workspace/script_detail.html", context=context)


# request is a required parameter
@own_basket_only
def script_raw(
    request: WSGIRequest,  # pylint: disable=unused-argument
    basket_id: int,
    script_id: int,
) -> HttpResponse:
    """ View of raw workspace.Script model """
    script = get_object_or_404(Script, pk=script_id)
    text = script.get_script_input()["text"]
    return HttpResponse(text, content_type="text/plain")


# request is a required parameter
@own_basket_only
def script_delete(
    request: WSGIRequest,  # pylint: disable=unused-argument
    basket_id: int,
    script_id: int,
) -> HttpResponseRedirect:
    """ Delete view for workspace.Script model """
    script = get_object_or_404(Script, pk=script_id)
    script.delete()
    return redirect("/workspace/baskets/%s" % basket_id)


# request is a required parameter
@own_basket_only
def script_new_lang(
    request: WSGIRequest,  # pylint: disable=unused-argument
    basket_id: int,
    generator_name: str,
):
    """ CreateView for a new Script """
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


# request is a required parameter
@own_basket_only
def script_new(request: WSGIRequest, basket_id: int):  # pylint: disable=unused-argument
    """ CreateView for a new Script """
    basket = get_object_or_404(Basket, pk=basket_id)
    script_count = basket.script_set.count() + 1
    script_name = f"script-{script_count}"
    script = Script.objects.create(
        name=script_name, basket_id=basket_id, settings=SoepStata.DEFAULT_CONFIG
    )
    return redirect(script.get_absolute_url())
