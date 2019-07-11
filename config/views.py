# -*- coding: utf-8 -*-

""" Views for ddionrails project """

from django.shortcuts import render
from django.views.generic.base import TemplateView

from ddionrails.studies.models import Study


# exception is a required parameter
def bad_request(request, exception):  # pylint: disable=unused-argument
    """ Custom HTTP 400 view """
    response = render(request, "400.html")
    response.status_code = 400
    return response


# exception is a required parameter
def permission_denied(request, exception):  # pylint: disable=unused-argument
    """ Custom HTTP 403 view """
    response = render(request, "403.html")
    response.status_code = 403
    return response


# exception is a required parameter
def page_not_found(request, exception):  # pylint: disable=unused-argument
    """ Custom HTTP 404 view """
    response = render(request, "404.html")
    response.status_code = 404
    return response


def server_error(request):
    """ Custom HTTP 500 view """
    response = render(request, "500.html")
    response.status_code = 500
    return response


class HomePageView(TemplateView):
    """ Renders a list of all available studies. """

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study_list"] = Study.objects.all()
        return context
