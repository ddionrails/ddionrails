# -*- coding: utf-8 -*-

""" Views for ddionrails.concepts app """

from django.views.generic import DetailView, ListView

from ddionrails.data.models import Variable
from ddionrails.instruments.models import Question

from .models import Concept


class ConceptListView(ListView):
    """ ListView for concepts.Concept model """

    model = Concept


class ConceptDetailView(DetailView):
    """ DetailView for concepts.Concept model """

    model = Concept
    template_name = "concepts/concept_detail.html"
    slug_url_kwarg = "concept_name"
    query_pk_and_slug = True
    slug_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        concept_id = context["concept"].pk
        context["variables"] = Variable.get_by_concept_id(concept_id).select_related(
            "dataset", "dataset__study"
        )
        context["questions"] = (
            Question.objects.filter(concepts_questions__concept_id=concept_id)
            .all()
            .select_related("instrument")
        )
        return context
