import os
import pprint

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from data.models import Dataset, Variable
from instruments.models import Instrument, Question

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
        context["num_datasets"] = Dataset.objects.filter(study=self.object).count()
        context["num_variables"] = Variable.objects.filter(
            dataset__study=self.object
        ).count()
        context["num_instruments"] = Instrument.objects.filter(study=self.object).count()
        context["num_questions"] = Question.objects.filter(
            instrument__study=self.object
        ).count()

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
                "conceptual_dataset__label",
                "period__name",
                "period__label",
                "analysis_unit__name",
                "analysis_unit__label",
            )
        )
        context["instrument_list"] = (
            Instrument.objects.select_related("study", "period", "analysis_unit")
            .filter(study=self.object)
            .only(
                "name",
                "label",
                "study__name",
                "period__name",
                "period__label",
                "analysis_unit__name",
                "analysis_unit__label",
            )
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
    return render(request, "studies/study_topics.html", context=context)
