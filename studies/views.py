import os
import pprint

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from data.models import Dataset
from instruments.models import Instrument

from .models import Study


class StudyRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        study = get_object_or_404(Study, id=kwargs["id"])
        return study.get_absolute_url()


class StudyDetailView(DetailView):
    model = Study
    template_name = "studies/study_detail.html"
    slug_url_kwarg = "study_name"
    slug_field = "name"

    def get_queryset(self):
        queryset = super(StudyDetailView, self).get_queryset()
        return queryset.only("name", "label", "config", "description")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dataset_list"] = (
            Dataset.objects.select_related(
                "study", "conceptual_dataset", "period", "analysis_unit"
            )
            .filter(study=self.object)
            .only(
                "name",
                "label",
                "study__name",
                "conceptual_dataset__name",
                "period__name",
                "analysis_unit__name",
            )
        )
        context["instrument_list"] = (
            Instrument.objects.select_related("study", "period", "analysis_unit")
            .filter(study=self.object)
            .only("name", "label", "study__name", "period__name", "analysis_unit__name")
        )
        context["debug_string"] = pprint.pformat(
            dict(
                name=self.object.name,
                config=self.object.get_config(),
                source=self.object.get_source(),
                getcwd=os.getcwd(),
            )
        )
        return context


def study_topics(request: HttpRequest, study_name: str, language: str) -> HttpResponse:
    study = get_object_or_404(Study, name=study_name)
    context = dict(study=study, language=language)
    # context["hide_topics"] = len(context["topics"]) == 0
    return render(request, "studies/study_topics.html", context=context)


def study_topics2(request, study_name, language):
    study = get_object_or_404(Study, name=study_name)
    context = dict(study=study, language=language)
    # context["hide_topics"] = len(context["topics"]) == 0
    return render(request, "studies/study_topics_extra_div.html", context=context)
