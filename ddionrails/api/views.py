# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """

import difflib
import re
import uuid
from typing import List

import yaml
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.mail import send_mail
from django.db.models import Model, Q, QuerySet
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from config.settings.base import DEFAULT_FEEDBACK_TO_EMAIL
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
from ddionrails.instruments.models.question import Question
from ddionrails.instruments.views import get_question_item_metadata
from ddionrails.statistics.models import StatisticsMetadata, VariableStatistic
from ddionrails.studies.models import Study
from ddionrails.workspace.models.basket import Basket
from ddionrails.workspace.models.basket_variable import BasketVariable

# VIEWS


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


class StatisticsMetadataViewSet(viewsets.GenericViewSet):
    """List metadata for a variables statistical data."""

    queryset = StatisticsMetadata.objects.all()

    @staticmethod
    def list(request: Request) -> Response:
        """Retrieve metadata and serve as response."""
        variable_id = request.query_params.get("variable", None)
        if not variable_id:
            return Response({})
        metadata = StatisticsMetadata.objects.filter(variable__id=variable_id).first()
        if not metadata:
            raise Http404

        return Response(metadata.metadata)


class StatisticViewSet(viewsets.GenericViewSet):
    """Display the statistical data in form of csv files."""

    queryset = VariableStatistic.objects.all()

    @staticmethod
    def list(request: Request) -> HttpResponse:
        """Retrieve the statistical data in form of csv files."""
        variable_id = request.query_params.get("variable", None)
        if (
            "dimensions" in request.query_params
            and request.query_params["dimensions"] != ""
        ):
            dimensions = sorted(request.query_params["dimensions"].split(","))
        else:
            dimensions = []
        _type = request.query_params.get("type", None)
        variable = get_object_or_404(Variable, id=variable_id)
        variable_statistic = VariableStatistic.objects.get(
            variable__id=variable_id,
            independent_variable_names=dimensions,
            plot_type=_type,
        )
        response = HttpResponse(variable_statistic.statistics, content_type="text/csv")
        response["Content-Disposition"] = f"attachement; filename={variable.label}.csv"

        return response


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
# Propper REST views start here


class StudyViewSet(viewsets.ModelViewSet):
    """List metadata about all studies."""

    queryset = Study.objects.all()
    serializer_class = StudySerializer


class VariableViewSet(viewsets.ModelViewSet):
    """List metadata about all variables."""

    serializer_class = VariableSerializer

    @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Variable]:
        topic = self.request.query_params.get("topic", None)
        concept = self.request.query_params.get("concept", None)
        study = self.request.query_params.get("study", None)
        statistics_data = self.request.query_params.get("statistics", False)

        paginate = self.request.query_params.get("paginate", "False")
        if paginate == "False":
            self.pagination_class = None

        queryset_filter = {}
        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if topic:
            if study:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                queryset_filter["concept__in"] = Concept.objects.filter(
                    topics__in=topic_object.get_topic_tree_leaves()
                ).distinct()
            else:
                raise NotAcceptable(
                    detail=(
                        "Topic parameter requires study parameter to be present as well."
                    )
                )
        if concept:
            concept_object = get_object_or_404(Concept, name=concept)
            queryset_filter["concept"] = concept_object
        if study:
            study_object = get_object_or_404(Study, name=study)
            queryset_filter["dataset__study"] = study_object
        if statistics_data:
            return (
                Variable.objects.filter(**queryset_filter)
                .exclude(statistics_data=None)
                .select_related("dataset", "dataset__study")
                .prefetch_related("statistics_data")
            )

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
        queryset_filter = {}
        if topic and concept:
            raise NotAcceptable(
                detail="Concept and topic are mutually exclusive parameters."
            )

        if topic:
            if study:
                topic_object: Topic = get_object_or_404(
                    Topic, name=topic, study__name=study
                )
                concepts = Concept.objects.filter(
                    topics__in=topic_object.get_topic_tree_leaves()
                ).distinct()
                queryset_filter["concepts_questions__concept__in"] = concepts
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
        query_filter = {}
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
    """Limit creation and deletion premissions of BasketVariables.

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

    def _basket_limit_error_message(self, basket_size: int, variables: int) -> str:
        return (
            f"The basket contains {basket_size} variables, adding {variables}"
            f"variables would exceed the basket size limit of {self.basket_limit}."
        )

    @property
    def basket_limit(self):
        """The global size limit for all Baskets."""
        return self.BASKET_LIMIT

    def get_queryset(self):
        _filter = {}
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
        basket_variables = []
        basket_size = BasketVariable.objects.filter(basket=basket.id).count()

        self._test_exclusivity(["variables" in data, "concept" in data, "topic" in data])

        variable_filter = {}

        if "variables" in data:
            variable_filter = {"id__in": data["variables"]}

        if "topic" in data:
            topic_object: Topic = Topic.objects.get(
                name=data["topic"], study=basket.study
            )
            variable_filter = {
                "concept__topics__in": topic_object.get_topic_tree_leaves()
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


class EmailThrottle(AnonRateThrottle):
    """Sets custom throttling rate through the settings."""

    scope = "sendmail"


class SendFeedback(APIView):
    """Process feedback form content to send feedback mails."""

    throttle_classes = [EmailThrottle]

    @staticmethod
    def get_queryset() -> QuerySet[Model]:
        """ApiView needs a queryset so we return an empty one here."""
        return Variable.objects.none()

    def post(self, request: Request) -> Response:
        """Process posted form data."""
        form_data = request.data
        if "anon-submit-button" in form_data:
            email = "Anonym"
        else:
            email = form_data["email"]

        feedback = form_data["feedback"]

        if form_data["source"]:
            source = form_data["source"]
        else:
            source = "Es wurde kein Suchstring angegeben."

        message = f"""Feedback kommt von {email}

        URL: {source}
        
        {feedback}
        """

        send_mail(
            f"Paneldata Suche Feedback: {form_data['feedback-type']}",
            message,
            None,
            [DEFAULT_FEEDBACK_TO_EMAIL],
            fail_silently=True,
        )
        return Response(str(request.data))
