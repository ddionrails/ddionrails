# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """

import uuid
from typing import List

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ddionrails.api.serializers import (
    BasketHyperlinkedSerializer,
    BasketVariableSerializer,
    QuestionSerializer,
    StudySerializer,
    UserSerializer,
    VariableSerializer,
)
from ddionrails.concepts.models import Concept, Topic
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.models import Question
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable

# VIEWS


class TopicTreeViewSet(viewsets.GenericViewSet):
    """Retrieve the topic tree of a study from a JSON field."""

    queryset = Study.objects.all()

    @staticmethod
    def list(request):
        """Read query parameters and return response or 404 if study does not exist."""
        study = request.query_params.get("study", None)
        language = request.query_params.get("language", "en")
        study_object = get_object_or_404(Study, name=study)

        return Response(study_object.get_topiclist(language))


# pylint: disable=too-many-ancestors
# Propper REST views start here


class StudyViewSet(viewsets.ModelViewSet):
    """List metadata about all studies."""

    queryset = Study.objects.all()
    serializer_class = StudySerializer


class VariableViewSet(viewsets.ModelViewSet):
    """List metadata about all variables."""

    serializer_class = VariableSerializer

    def get_queryset(self):
        topic = self.request.query_params.get("topic", None)
        concept = self.request.query_params.get("concept", None)
        study = self.request.query_params.get("study", None)
        if not self.request.query_params.get("paginate", False):
            self.pagination_class = None

        queryset_filter = dict()
        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if topic:
            if study:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                children = [
                    topic.id
                    for topic in topic_object.get_topic_tree_leaves(
                        topic_object=topic_object
                    )
                ]
                queryset_filter["concept__topics__id__in"] = children
            else:
                raise NotAcceptable(
                    detail=(
                        "Topic parameter requires study parameter to be present as well."
                    )
                )
        if concept:
            concept_object = get_object_or_404(Concept, name=concept)
            queryset_filter["concept_id"] = concept_object.id
        if study:
            study_object = get_object_or_404(Study, name=study)
            queryset_filter["dataset__study_id"] = study_object.id

        return Variable.objects.filter(**queryset_filter).select_related(
            "dataset", "dataset__study"
        )


class QuestionViewSet(viewsets.ModelViewSet):
    """List metadata about all variables."""

    serializer_class = QuestionSerializer
    pagination_class = None

    def get_queryset(self):
        topic = self.request.query_params.get("topic", None)
        concept = self.request.query_params.get("concept", None)
        study = self.request.query_params.get("study", None)
        queryset_filter = dict()
        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if topic:
            if study:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                children = [
                    topic.id
                    for topic in topic_object.get_topic_tree_leaves(
                        topic_object=topic_object
                    )
                ]
                queryset_filter["concepts_questions__concept__topics__id__in"] = children
            else:
                raise NotAcceptable(
                    detail=(
                        "Topic parameter requires study parameter to be present as well."
                    )
                )
        if concept:
            concept_object = get_object_or_404(Concept, name=concept)
            queryset_filter["concepts_questions__concept__id"] = concept_object.id
        if study:
            study_object = get_object_or_404(Study, name=study)
            queryset_filter["instrument__study_id"] = study_object.id

        return Question.objects.filter(**queryset_filter).select_related(
            "instrument", "instrument__study"
        )


class BasketViewSet(viewsets.ModelViewSet, CreateModelMixin, DestroyModelMixin):
    """List baskets or create a single basket.

    Baskets are returned according to permissions.
    Normal users can only retrieve their own baskets.
    Superusers can retrieve all baskets.

    Basket creation is the similar.
    Normal users can create baskets for themselves.
    Superusers can create baskets for arbitrary users.
    """

    serializer_class = BasketHyperlinkedSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """get queryset according to permissions."""
        user = self.request.user
        study = self.request.query_params.get("study", None)
        query_filter = dict()
        if study:
            query_filter["study__name"] = study
        return Basket.objects.filter(user=user.id, **query_filter)

    def create(self, request, *args, **kwargs):
        """Create a single basket."""
        data = request.data
        basket_user = data["user_id"]
        user = request.user

        if basket_user != user.id and not user.is_superuser:
            raise PermissionDenied(detail="Permission on users baskets denied.")

        basket, created = Basket.objects.get_or_create(
            name=data["name"], user_id=data["user_id"], study_id=data["study_id"]
        )

        if not created:
            return Response(
                {
                    "detail": (
                        "This user already owns a basket of that name for this study."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        basket.label = data["label"]
        basket.description = data["description"]
        basket.save()

        serializer = self.serializer_class(basket, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IsBasketOwner(permissions.BasePermission):
    """ Limit creation and deletion premissions of BasketVariables.

    Users should only be allowed to create or delete BasketVariables for Baskets that
    they own.

    Superusers are exempt and can manipulate all BasketVariables.
    """

    @staticmethod
    def has_permission(request, view):
        if request.user.is_superuser:
            return True
        if request.method == "POST":
            if "basket" in request.data:
                basket = Basket.objects.get(id=request.data["basket"])
                return basket.user == request.user
            return False
        return True

    @staticmethod
    def has_object_permission(request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.basket.user == request.user


class BasketVariableSet(viewsets.ModelViewSet, CreateModelMixin):
    """List metadata about Baskets depending on user permissions."""

    queryset = BasketVariable.objects.all().select_related("basket", "variable")
    serializer_class = BasketVariableSerializer
    permission_classes = (IsAuthenticated, IsBasketOwner)
    BASKET_LIMIT = 1000

    DATA_MISSING_ERROR_MESSAGE = (
        "No set of variables was specified. "
        "To add variables to a basket specify either a list of variables, "
        "a topic or a concept fr9om which to add variables."
    )

    def _basket_limit_error_message(self, basket_size: int, variables: int):
        return (
            f"The basket contains {basket_size} variables, adding {variables}"
            f"variables would exceed the basket size limit of {self.basket_limit}."
        )

    @property
    def basket_limit(self):
        """The global size limit for all Baskets."""
        return self.BASKET_LIMIT

    def get_queryset(self):
        _filter = dict()
        basket = self.request.query_params.get("basket", None)
        variable = self.request.query_params.get("variable", None)

        if basket and variable:
            _filter["basket_id"] = basket
            _filter["variable_id"] = uuid.UUID(variable)

        if self.request.method == "GET":
            user = self.request.user
            if not user.is_superuser:
                _filter["basket__user"] = user.id

        return self.queryset.filter(**_filter)

    def create(self, request, *args, **kwargs):
        data = self.request.data

        if "basket" not in data:
            raise NotAcceptable(detail="Target basket needs to be specified.")

        basket = Basket.objects.get(id=data.get("basket"))
        basket_variables = list()
        basket_size = BasketVariable.objects.filter(basket=basket.id).count()

        self._test_exclusivity(["variables" in data, "concept" in data, "topic" in data])

        variable_filter = dict()

        if "variables" in data:
            variable_filter = {"id__in": data["variables"]}

        if "topic" in data:
            topic = Topic.objects.get(name=data["topic"], study=basket.study).id
            variable_filter = {
                "concept__topics__in": Topic.get_topic_tree_leaves(topic_object=topic)
            }

        if "concept" in data:
            concept = Concept.objects.get(name=data["concept"])
            variable_filter = {"concept": concept}

        if "study" in data:
            variable_filter["dataset__study__name"] = data["study"]

        variables = Variable.objects.filter(
            ~Q(baskets_variables__basket=basket), **variable_filter
        )

        if len(variables) + basket_size > self.basket_limit:
            raise NotAcceptable(
                detail=self._basket_limit_error_message(basket_size, len(variables))
            )
        for variable in variables:
            basket_variables.append(BasketVariable(variable=variable, basket=basket))

        BasketVariable.objects.bulk_create(basket_variables)
        if len(variables) == 0:
            return Response(
                {"detail": "No new variables to add to this Basket."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Successfully added "
                + str(len(variables))
                + " variables to this Basket."
            },
            status=status.HTTP_201_CREATED,
        )

    def _test_exclusivity(self, values: List[bool]) -> bool:
        """Check if only one boolean in list of booleans is True."""
        mutually_exclusive_violation = 0
        for value in values:
            mutually_exclusive_violation += value
        if mutually_exclusive_violation > 1:
            raise NotAcceptable(
                detail="Keys topic, concept and variables are mutually exclusive."
            )
        if mutually_exclusive_violation == 0:
            raise NotAcceptable(detail=self.DATA_MISSING_ERROR_MESSAGE)


class UserViewSet(viewsets.ModelViewSet):
    """List user metadata for admin users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
