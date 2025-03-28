""" Basic views not associated directly with any study. """

from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study


def imprint(request, template_name="pages/imprint.html"):
    """Display imprint view."""
    context = {
        "INSTITUTE_NAME": settings.INSTITUTE_NAME,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "INSTITUTE_HOME_URL": settings.INSTITUTE_HOME_URL,
        "PRIVACY_POLICY": settings.PRIVACY_POLICY,
    }
    return TemplateResponse(request, template_name, context)


def pid(request, template_name="pages/pid_archive.html"):
    """Redirect PID requests."""
    # TODO: Remove comment after testing. pylint: disable=fixme
    # if "labs.da-ra.de" not in request.META.get("HTTP_REFERER", ""):
    #   return HttpResponseNotFound()
    if request.method != "GET":
        return HttpResponseNotFound()
    context = {}
    context["study"] = request.GET.get("study")
    context["dataset"] = request.GET.get("dataset")
    context["version"] = request.GET.get("version")
    context["variable"] = request.GET.get("variable")

    study = get_object_or_404(Study, name=context["study"])

    try:
        variable = Variable.objects.get(
            dataset__study__name=context["study"],
            dataset__name=context["dataset"],
            name=context["variable"],
        )
    except Variable.DoesNotExist:
        return TemplateResponse(request, template_name, context)

    if study.version != context["version"]:
        context["url"] = variable.get_absolute_url()
        context["current_version"] = study.version
        return TemplateResponse(request, template_name, context)

    return redirect(variable)
