# -*- coding: utf-8 -*-
"""Views for ddionrails.api app"""

import difflib
import re
from typing import Any

import yaml
from django.db.models import QuerySet
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from ddionrails.api.serializers import InstrumentSerializer, QuestionSerializer
from ddionrails.api.views.parameters_definition import (
    CONCEPT_PARAMETER,
    INSTRUMENT_PARAMETER,
    PAGINATE_PARAMETER,
    STUDY_PARAMETER,
    TOPIC_PARAMETER,
    VARIABLES_PARAMETER,
)
from ddionrails.concepts.models import Concept, Topic
from ddionrails.instruments.models.question import Instrument, Question
from ddionrails.instruments.views import get_question_item_metadata
from ddionrails.studies.models import Study


@extend_schema(exclude=True)
class QuestionComparisonViewSet(viewsets.GenericViewSet):
    """Retrieve question and item metadata combined."""

    queryset = Question.objects.none()

    @staticmethod
    def list(request: Request) -> HttpResponse:
        """Retrieve question via id and return metadata"""
        questions_ids = request.query_params.get("questions", "").split(",")
        if len(questions_ids) != 2 or "" in questions_ids:
            raise Http404
        ours_question = get_object_or_404(
            Question.objects.select_related("instrument", "instrument__period"),
            pk=questions_ids[0],
        )
        theirs_question = get_object_or_404(
            Question.objects.select_related("instrument", "instrument__period"),
            pk=questions_ids[1],
        )
        ours_metadata = re.sub(
            r"((^\W+)|(\n\W+))",
            "\n",
            yaml.dump(
                get_question_item_metadata(ours_question, short=True),
                sort_keys=False,
                allow_unicode=True,
                width=float("inf"),
            ),
        )[1:]
        theirs_metadata = re.sub(
            r"((^\W+)|(\n\W+))",
            "\n",
            yaml.dump(
                get_question_item_metadata(theirs_question, short=True),
                sort_keys=False,
                allow_unicode=True,
                width=float("inf"),
            ),
        )[1:]

        diff = difflib.HtmlDiff().make_table(
            ours_metadata.split("\n"),
            theirs_metadata.split("\n"),
            fromdesc=(
                f"{ours_question.instrument.period.name}: "
                f"{ours_question.instrument.name}/{ours_question.name}"
            ),
            todesc=(
                f"{theirs_question.instrument.period.name}: "
                f"{theirs_question.instrument.name}/{theirs_question.name}"
            ),
        )

        return HttpResponse(diff, content_type="text/html")


@extend_schema(
    parameters=[
        STUDY_PARAMETER,
        PAGINATE_PARAMETER,
    ]
)
class InstrumentViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List metadata about all instruments."""

    serializer_class = InstrumentSerializer
    http_method_names = ["get"]

    @method_decorator(cache_page(60 * 60 * 2, cache="instrument_api"))
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Instrument]:
        _filter = {}
        paginate = self.request.query_params.get("paginate", "True")
        if paginate == "False":
            self.pagination_class = None
        if study_name := self.request.query_params.get("study", None):
            _filter["study__name"] = study_name

        instruments: QuerySet[Instrument] = (  # To help mypy recognize return type
            Instrument.objects.filter(**_filter)
            .select_related("period", "analysis_unit")
            .prefetch_related("attachments")
        )
        return instruments


@extend_schema(
    parameters=[
        STUDY_PARAMETER,
        PAGINATE_PARAMETER,
        INSTRUMENT_PARAMETER,
        TOPIC_PARAMETER,
        CONCEPT_PARAMETER,
        VARIABLES_PARAMETER,
    ]
)
class QuestionViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List metadata about all questions."""

    serializer_class = QuestionSerializer
    pagination_class = None
    http_method_names = ["get"]

    def get_queryset(self):
        topic = self.request.query_params.get("topic", None)
        concept = self.request.query_params.get("concept", None)
        instrument = self.request.query_params.get("instrument", None)
        study = self.request.query_params.get("study", None)
        variables = self.request.query_params.getlist("variables[]", None)

        if instrument is None and topic is None and concept is None and variables is None:
            raise PermissionDenied()
        queryset_filter = {}

        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if variables:
            queryset_filter["questions_variables__variable__name__in"] = variables

        if study:
            study_object = get_object_or_404(Study, name=study)
            queryset_filter["instrument__study"] = study_object

            if topic:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                concepts = Concept.objects.filter(
                    topics__in=topic_object.get_topic_tree_leafs()
                ).distinct()
                queryset_filter["concepts_questions__concept__in"] = concepts
            if instrument:
                dataset_object: Instrument = get_object_or_404(
                    Instrument, name=instrument, study__name=study
                )
                queryset_filter["instrument"] = dataset_object
        elif topic or instrument:
            raise NotAcceptable(
                detail=(
                    "Topic and Instrument parameter requires "
                    "study parameter to be present as well."
                )
            )

        if concept:
            concept_object = get_object_or_404(Concept, name=concept)
            queryset_filter["concepts_questions__concept__id"] = concept_object.id

        return (
            Question.objects.filter(**queryset_filter)
            .select_related("instrument", "instrument__study")
            .distinct()
        )
