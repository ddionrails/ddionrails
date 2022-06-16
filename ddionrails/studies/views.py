# -*- coding: utf-8 -*-

""" Views for ddionrails.studies app """

from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView

from ddionrails.data.models import Dataset, Variable
from ddionrails.instruments.models import Instrument, Question

from .models import Study


class StudyDetailView(DetailView):
    """DetailView for studies.Study model"""

    model = Study
    template_name = "studies/study_detail.html"
    slug_url_kwarg = "study_name"
    slug_field = "name"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.only("name", "label", "config", "description")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["num_datasets"] = Dataset.objects.filter(study=self.object).count()
        context["num_variables"] = Variable.objects.filter(
            dataset__study=self.object
        ).count()
        context["num_instruments"] = Instrument.objects.filter(study=self.object).count()
        context["num_questions"] = Question.objects.filter(
            instrument__study=self.object
        ).count()

        context["has_extended_metadata"] = (
            Instrument.objects.filter(
                Q(study__name=context["study"]) & ~Q(mode="")
            ).count()
            > 0
        )

        return context


def study_topics(request: HttpRequest, study_name: str, language: str) -> HttpResponse:
    """Display topic tree for a study."""
    study = get_object_or_404(Study, name=study_name)
    context = dict(
        study=study,
        language=language,
        json_object={"study": study.name, "language": language},
    )
    context["namespace"] = "topics"
    return render(request, "studies/study_topics.html", context=context)
