# -*- coding: utf-8 -*-

""" Views for ddionrails.instruments app """

from re import sub
from typing import Dict, List

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView
from django.views.generic.base import RedirectView

from config.helpers import RowHelper
from ddionrails.data.models import Variable
from ddionrails.instruments.models import Instrument, Question, QuestionItem
from ddionrails.instruments.models.question_item import QuestionItemDict
from ddionrails.studies.models import Study
from ddionrails.studies.views import get_study_context

NAMESPACE = "instruments"


class InstrumentRedirectView(RedirectView):
    """RedirectView for instruments.Instrument model"""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        instrument = get_object_or_404(Instrument, id=kwargs["id"])
        return instrument.get_absolute_url()


# Disable pylint warning since DetailView comes from django.
class InstrumentDetailView(DetailView):  # pylint: disable=too-many-ancestors
    """DetailView for instruments.Instrument model"""

    template_name = "instruments/instrument_detail.html"

    def get_object(self, queryset=None):
        instrument = get_object_or_404(
            Instrument.objects.select_related("period"),
            study=self.kwargs["study"],
            name=self.kwargs["instrument_name"],
        )
        return instrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = self.object.study
        context["namespace"] = NAMESPACE
        return context


class AllStudyInstrumentsView(TemplateView):  # pylint: disable=too-many-ancestors
    """Table with all instruments of a study."""

    template_name = f"{NAMESPACE}/study_instruments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = kwargs["study"]
        context["namespace"] = NAMESPACE
        context["has_extended_metadata"] = (
            Instrument.objects.filter(Q(study=context["study"]) & ~Q(mode="")).count() > 0
        )
        context = context | get_study_context(Study.objects.get(name=kwargs["study"]))
        return context


class InstRedirectView(RedirectView):
    """RedirectView for instruments.Question model"""

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        uri = self.request.build_absolute_uri()
        uri = sub("/inst/", "/instruments/", uri)
        return uri


class QuestionRedirectView(RedirectView):
    """RedirectView for instruments.Question model"""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        question = get_object_or_404(Question, id=kwargs["id"])
        return question.get_absolute_url()


# request is a required parameter
def question_detail(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study: str,
    instrument_name: str,
    question_name: str,
) -> HttpResponse:
    """DetailView for instruments.question model"""
    question = Question.objects.select_related(
        "instrument",
        "instrument__study",
        "instrument__period",
        "instrument__analysis_unit",
    ).get(
        instrument__study=study,
        instrument__name=instrument_name,
        name=question_name,
    )
    question_items = get_question_item_metadata(question)

    concept_list = question.get_concepts()
    context = {
        "question": question,
        "study": question.instrument.study,
        "concept_list": concept_list,
        "variables": Variable.objects.filter(
            questions_variables__question=question.id
        ).select_related("dataset", "dataset__study"),
        "base_url": f"{request.scheme}://{request.get_host()}",
        "related_questions": question.get_related_questions(),
        "row_helper": RowHelper(),
        "question_items": question_items,
    }

    return render(request, "questions/question_detail.html", context=context)


def get_question_item_metadata(
    question: Question, short: bool = False
) -> List[List[QuestionItemDict]]:
    """Get metadata for a question and all it's items."""
    question_items = list(
        question.question_items.all()
        .order_by("position")
        .prefetch_related("answers")
        .distinct()
    )
    block_counter = 0
    blocks = {block_counter: [question_items.pop(0)]}
    for item in question_items:
        if _blocks_equal(item, blocks[block_counter][-1]):
            blocks[block_counter].append(item)
            continue
        block_counter += 1
        blocks[block_counter] = [item]

    return _serialize_blocks(blocks, short)


def _serialize_blocks(
    blocks: Dict[int, List[QuestionItem]], short: bool = False
) -> List[List[QuestionItemDict]]:

    serialized: List[List[QuestionItemDict]]
    serialized = [[] for position in range(0, len(blocks))]
    for position, block in blocks.items():
        for item in block:
            serialized[position].append(item.to_dict(short))

    return serialized


def _blocks_equal(item: QuestionItem, block_item: QuestionItem) -> bool:
    if item.scale == block_item.scale == "cat":
        if _answers_equal(item, block_item):
            return True
        return False
    if item.scale in ["chr", "int", "bin"] and item.scale == block_item.scale:
        return True
    return False


def _answers_equal(item: QuestionItem, other_item: QuestionItem) -> bool:
    return list(item.answers.all().order_by("value")) == list(
        other_item.answers.all().order_by("value")
    )
