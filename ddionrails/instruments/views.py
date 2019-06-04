# -*- coding: utf-8 -*-

import difflib

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from config.helpers import RowHelper
from ddionrails.data.models import Variable
from ddionrails.studies.models import Study

from .models import Instrument, Question


def study_instrument_list(request: WSGIRequest, study_name: str):
    study = get_object_or_404(Study, name=study_name)
    context = dict(
        study=study, instrument_list=Instrument.objects.filter(study__name=study_name)
    )
    return render(request, "instruments/study_instrument_list.html", context=context)


class InstrumentRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        instrument = get_object_or_404(Instrument, pk=kwargs["pk"])
        return instrument.get_absolute_url()


class InstrumentDetailView(DetailView):
    template_name = "instruments/instrument_detail.html"

    def get_object(self, queryset=None):
        instrument = get_object_or_404(
            Instrument,
            study__name=self.kwargs["study_name"],
            name=self.kwargs["instrument_name"],
        )
        return instrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = self.object.study
        context["questions"] = context["instrument"].questions.all()
        return context


class QuestionRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs["pk"])
        return question.get_absolute_url()


def question_detail(request, study_name, instrument_name, question_name):
    question = (
        Question.objects.filter(instrument__study__name=study_name)
        .filter(instrument__name=instrument_name)
        .get(name=question_name)
    )

    concept_list = question.get_concepts()
    try:
        related_questions = Question.objects.filter(
            items__items_variables__variable__concept_id__in=[
                concept.id for concept in concept_list
            ]
        ).distinct()
    except:
        related_questions = []
    context = dict(
        question=question,
        study=question.instrument.study,
        concept_list=concept_list,
        related_questions=related_questions,
        variables=Variable.objects.filter(questions_variables__question=question.id),
        related_questions2=question.get_related_question_set(by_study_and_period=True)[
            question.instrument.study.name
        ],
        row_helper=RowHelper(),
    )
    return render(request, "questions/question_detail.html", context=context)


def question_comparison_partial(request: WSGIRequest, from_id: int, to_id: int):
    from_question = get_object_or_404(Question, pk=from_id)
    to_question = get_object_or_404(Question, pk=to_id)
    diff_text = difflib.HtmlDiff().make_file(
        from_question.comparison_string(),
        to_question.comparison_string(),
        fromdesc=from_question.name,
        todesc=to_question.name,
    )
    return HttpResponse(diff_text)
