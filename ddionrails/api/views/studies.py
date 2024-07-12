# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """


from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from ddionrails.api.serializers import StudySerializer
from ddionrails.concepts.models import Topic
from ddionrails.studies.models import Study


class TopicTreeViewSet(viewsets.GenericViewSet):
    """Retrieve the topic tree of a study from a JSON field."""

    queryset = Study.objects.all()

    @staticmethod
    def list(request: Request) -> Response:
        """Read query parameters and return response or 404 if study does not exist."""
        study = request.query_params.get("study", None)
        language = request.query_params.get("language", "en")
        study_object = get_object_or_404(Study, name=study)

        return Response(study_object.get_topiclist(language))


# pylint: disable=too-many-ancestors
# Proper REST views start here


class TopicRootAndLeaves(viewsets.GenericViewSet):
    queryset = Study.objects.all()

    @staticmethod
    def list(request: Request) -> Response:
        """Read query parameters and return response or 404 if study does not exist."""
        study = request.query_params.get("study", None)
        language = request.query_params.get("language", "en")
        language_prefix = ""
        if language == "de":
            language_prefix = "_de"
        study_object = get_object_or_404(Study, name=study)
        root_topics = Topic.objects.filter(study=study_object, parent=None)
        output = {}
        for topic in root_topics:
            topic: Topic
            leaves = topic.get_topic_tree_leaves()
            output[topic.name] = {
                "label": getattr(topic, f"label{language_prefix}"),
                "children": [
                    getattr(leave, f"label{language_prefix}") for leave in leaves
                ],
            }

        return Response(output)


class StudyViewSet(viewsets.ModelViewSet):
    """List metadata about all studies."""

    queryset = Study.objects.all()
    serializer_class = StudySerializer
