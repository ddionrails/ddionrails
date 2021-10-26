# -*- coding: utf-8 -*-

""" Views for ddionrails.instruments app """

import difflib
import uuid
from typing import Dict, List, TypedDict

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from config.helpers import RowHelper
from ddionrails.data.models import Variable
from ddionrails.instruments.models import (
    Instrument,
    Question,
    QuestionImage,
    QuestionItem,
)
from ddionrails.instruments.models.question_item import QuestionItemDict
from ddionrails.studies.models import Study


# request is a required parameter
def study_instrument_list(
    request: WSGIRequest, study_name: str  # pylint: disable=unused-argument
) -> HttpResponse:
    """Render instruments of a study from template. """
    study = get_object_or_404(Study, name=study_name)
    context = dict(
        study=study, instrument_list=Instrument.objects.filter(study__name=study_name)
    )
    return render(request, "instruments/study_instrument_list.html", context=context)


class InstrumentRedirectView(RedirectView):
    """ RedirectView for instruments.Instrument model """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        instrument = get_object_or_404(Instrument, id=kwargs["id"])
        return instrument.get_absolute_url()


# Disable pylint warning since DetailView comes from django.
class InstrumentDetailView(DetailView):  # pylint: disable=too-many-ancestors
    """ DetailView for instruments.Instrument model """

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
    """ RedirectView for instruments.Question model """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        question = get_object_or_404(Question, id=kwargs["id"])
        return question.get_absolute_url()


# request is a required parameter
def question_detail(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str = None,
    instrument_name: str = None,
    question_name: str = None,
):
    """ DetailView for instruments.question model """
    question = Question.objects.select_related(
        "instrument",
        "instrument__study",
        "instrument__period",
        "instrument__analysis_unit",
    ).get(
        instrument__study__name=study_name,
        instrument__name=instrument_name,
        name=question_name,
    )
    question_items = _question_item_metadata(question)

    concept_list = question.get_concepts()
    context = dict(
        question=question,
        study=question.instrument.study,
        concept_list=concept_list,
        variables=Variable.objects.filter(
            questions_variables__question=question.id
        ).select_related("dataset", "dataset__study"),
        base_url=f"{request.scheme}://{request.get_host()}",
        related_questions=question.get_related_questions(),
        row_helper=RowHelper(),
        question_items=question_items,
    )
    # TODO: Language setup is not centralized. There is no global switch.
    # This would have to be overhauled if the a global switch is implemented.
    images = QuestionImage.objects.filter(question_id=question.id).all()

    class ImageContextMapping(TypedDict, total=False):
        """Typing for image metadata"""

        image_label: str  # One label for both languages
        en: str  # URL of english image
        de: str  # URL of german image

    image_context: ImageContextMapping = ImageContextMapping()
    for _image in images:
        image_context[_image.language] = settings.MEDIA_URL + str(_image.image.file)
        # English label will be default label without global switch.
        # German label is the fallback if no english image exists.
        if _image.language == "en":
            image_context["image_label"] = _image.label
        elif "image_label" not in image_context:
            image_context["image_label"] = _image.label

    context["image_urls"] = image_context
    return render(request, "questions/question_detail.html", context=context)


# request is a required parameter
# TODO: This is not integrated into rest of the system in a way that is usable.
def question_comparison_partial(
    request: WSGIRequest,  # pylint: disable=unused-argument
    from_id: uuid.UUID,
    to_id: uuid.UUID,
) -> HttpResponse:
    from_question = get_object_or_404(Question, pk=from_id)
    to_question = get_object_or_404(Question, pk=to_id)
    diff_text = difflib.HtmlDiff().make_file(
        from_question.comparison_string(),
        to_question.comparison_string(),
        fromdesc=from_question.name,
        todesc=to_question.name,
    )
    return HttpResponse(diff_text)


def _question_item_metadata(question: Question):
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

    return _serialize_blocks(blocks)


def _serialize_blocks(
    blocks: Dict[int, List[QuestionItem]]
) -> List[List[QuestionItemDict]]:

    serialized: List[List[QuestionItemDict]]
    serialized = [[] for position in range(0, len(blocks))]
    for position, block in blocks.items():
        for item in block:
            serialized[position].append(item.to_dict())

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
