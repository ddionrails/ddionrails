# -*- coding: utf-8 -*-

""" Views for ddionrails.publications app """

from urllib.parse import urlencode

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from ddionrails.studies.models import Study

from .models import Publication


class PublicationRedirectView(RedirectView):
    """ RedirectView for publications.Publication model """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        publication = get_object_or_404(Publication, id=kwargs["id"])
        return publication.get_absolute_url()


class PublicationDetailView(DetailView):
    """ DetailView for publications.Publication model """

    model = Publication
    template_name = "publications/publication_detail.html"

    def get_object(self, queryset=None):
        publication = get_object_or_404(
            Publication,
            name=self.kwargs["publication_name"],
            study__name=self.kwargs["study_name"],
        )
        return publication

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publication"] = self.object
        context["study"] = self.object.study
        return context


# request is a required parameter
def study_publication_list(
    request: WSGIRequest, study_name: str  # pylint: disable=unused-argument,
):
    study = get_object_or_404(Study, name=study_name)
    # e.g. Studies=["soep-is"]
    query_string = urlencode({"Studies": f'["{study.title()}"]'})
    # e.g. http://localhost/search/publications?Studies=["soep-is"]
    url = f"/search/publications?{query_string}"
    return redirect(url)
