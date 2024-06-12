# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """

from typing import Any, Dict

from django.db.models import QuerySet
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from ddionrails.api.serializers import (
    DatasetSerializer,
    StatisticsVariableSerializer,
    VariableLabelsSerializer,
    VariableSerializer,
)
from ddionrails.concepts.models import Concept, Topic
from ddionrails.data.models.dataset import Dataset
from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study


class VariableViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List metadata about all variables."""

    serializer_class = VariableSerializer

    @method_decorator(cache_page(60 * 2))
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Variable]:
        topic = self.request.query_params.get("topic", None)
        concept = self.request.query_params.get("concept", None)
        study = self.request.query_params.get("study", None)
        dataset = self.request.query_params.get("dataset", None)
        if dataset is None and topic is None and concept is None:
            raise PermissionDenied()
        statistics_data = self.request.query_params.get("statistics", False)

        paginate = self.request.query_params.get("paginate", "False")
        if paginate == "False":
            self.pagination_class = None

        queryset_filter: Dict[str, Any] = {}
        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if concept:
            concept_object = get_object_or_404(Concept, name=concept)
            queryset_filter["concept"] = concept_object

        if study:
            study_object = get_object_or_404(Study, name=study)
            queryset_filter["dataset__study"] = study_object

            if topic:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                queryset_filter["concept__topics__in"] = (
                    topic_object.get_topic_tree_leaves()
                )
            if dataset:
                dataset_object: Dataset = get_object_or_404(
                    Dataset, name=dataset, study__name=study
                )
                queryset_filter["dataset"] = dataset_object
        elif topic or dataset:
            raise NotAcceptable(
                detail=(
                    "Topic and Dataset parameter requires "
                    "study parameter to be present as well."
                )
            )

        if statistics_data:
            self.serializer_class = StatisticsVariableSerializer
            queryset_filter["statistics_flag"] = True

        return (
            Variable.objects.filter(**queryset_filter)
            .select_related("dataset", "dataset__study")
            .distinct()
        )


class VariableLabelsViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List label metadata about all variables."""

    queryset = Variable.objects.none()

    serializer_class = VariableLabelsSerializer

    def get_queryset(self) -> QuerySet[Variable]:
        study = self.request.query_params.get("study", None)
        concept = self.request.query_params.get("concept", None)

        if concept is None:
            raise Http404

        query = {"concept__name": concept}
        if study:
            query["study__name"] = study

        return Variable.objects.filter(**query).select_related("period")


class DatasetViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List metadata about all variables."""

    serializer_class = DatasetSerializer

    @method_decorator(cache_page(60 * 60 * 2, cache="dataset_api"))
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Dataset]:
        datasets: QuerySet[Dataset]  # To help mypy recognize return type
        _filter = {}
        if study_name := self.request.query_params.get("study", None):
            _filter["study__name"] = study_name

        paginate = self.request.query_params.get("paginate", "True")
        if paginate == "False":
            self.pagination_class = None

        datasets = (
            Dataset.objects.filter(**_filter)
            .select_related("period", "study", "analysis_unit", "conceptual_dataset")
            .prefetch_related("attachments")
        )

        return datasets
