# -*- coding: utf-8 -*-

"""Views for ddionrails.publications app"""

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from ddionrails.studies.models import Study

from .models import Publication


class PublicationRedirectView(RedirectView):
    """RedirectView for publications.Publication model"""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        publication = get_object_or_404(Publication, id=kwargs["id"])
        return publication.get_absolute_url()


class PublicationDetailView(DetailView):
    """DetailView for publications.Publication model"""

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


def study_publication_list(
    request: WSGIRequest, study_name: str  # pylint: disable=unused-argument,
):
    """Construct the redirect for study specific publication search."""
    study = get_object_or_404(Study, name=study_name)
    url = (
        "/search/publications?"
        "&filters[0][field]=study_name"
        f"&filters[0][values][0]={study.title()}&"
        "filters[0][type]=all&"
        "filters[0][persistent]=false"
    )
    return redirect(url)
