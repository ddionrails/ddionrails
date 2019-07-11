# -*- coding: utf-8 -*-

""" Views for ddionrails.concepts app """

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.views.generic import DetailView

from ddionrails.data.models import Variable
from ddionrails.instruments.models import Question

from .models import Concept


def concept_list(request: WSGIRequest):  # pylint: disable=unused-argument
    """ Redirect to concept search """
    url = "/search/concepts"
    return redirect(url)


class ConceptDetailView(DetailView):
    """ DetailView for concepts.Concept model """

    model = Concept
    template_name = "concepts/concept_detail.html"
    pk_url_kwarg = "id"  # use "id" in URLConf for lookup
    slug_url_kwarg = "concept_name"  # use "concept_name" in URLConf for lookup
    query_pk_and_slug = True
    slug_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        concept_id = context["concept"].id
        context["variables"] = Variable.get_by_concept_id(concept_id).select_related(
            "dataset", "dataset__study"
        )
        context["questions"] = (
            Question.objects.filter(concepts_questions__concept_id=concept_id)
            .all()
            .select_related("instrument")
        )
        return context
