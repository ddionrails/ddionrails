# -*- coding: utf-8 -*-
""" Study related API endpoints. """


from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from ddionrails.api.serializers import StudySerializer
from ddionrails.concepts.models import Topic
from ddionrails.studies.models import Study


@extend_schema(exclude=True)
class TopicTreeViewSet(viewsets.GenericViewSet):
    """Retrieve the topic tree of a study from a JSON field."""

    queryset = Study.objects.all()
    pagination_class = None

    @staticmethod
    def list(request: Request) -> Response:
        """Read query parameters and return response or 404 if study does not exist."""
        study = request.query_params.get("study", None)
        language = request.query_params.get("language", "en")
        study_object = get_object_or_404(Study, name=study)

        return Response(study_object.get_topiclist(language))


# pylint: disable=too-many-ancestors
# Proper REST views start here


@extend_schema(exclude=True)
class TopicRootAndLeafs(viewsets.GenericViewSet):
    """Return Topics and their leaf nodes."""

    queryset = Study.objects.all()

    @method_decorator(cache_page(60 * 2))
    def list(self, request: Request) -> Response:
        """Read query parameters and return response or 404 if study does not exist."""
        study = request.query_params.get("study", None)
        topic: str | None = request.query_params.get("topic", None)
        language = request.query_params.get("language")
        language_prefix = ""
        if language == "de":
            language_prefix = "_de"
        study_object = get_object_or_404(Study, name=study)
        if topic:
            root_topics = Topic.objects.filter(study=study_object, name=topic)
        else:
            root_topics = Topic.objects.filter(study=study_object, parent=None)
        output = {}
        for _topic in root_topics:
            _topic: Topic
            leafs = _topic.get_topic_tree_leafs()
            output[_topic.name] = {
                "label": getattr(_topic, f"label{language_prefix}"),
                "children": [getattr(leaf, f"label{language_prefix}") for leaf in leafs],
            }
            if not language:
                output[_topic.name]["children_de"] = [
                    getattr(leaf, "label_de") for leaf in leafs
                ]

        return Response(output)


class StudyViewSet(viewsets.ModelViewSet):
    """List metadata about all studies."""

    http_method_names = ["get"]
    queryset = Study.objects.all()
    serializer_class = StudySerializer
