# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """

import uuid
from typing import List

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.mail import send_mail
from django.db.models import Model, Q, QuerySet
from django.http import Http404
from django.http.response import HttpResponseRedirect
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from config.settings.base import DEFAULT_FEEDBACK_TO_EMAIL, FEEDBACK_TO_EMAILS
from ddionrails.api.serializers import (
    BasketHyperlinkedSerializer,
    BasketVariableSerializer,
    UserSerializer,
)
from ddionrails.concepts.models import Concept, Topic
from ddionrails.data.models.variable import Variable
from ddionrails.workspace.models.basket import Basket
from ddionrails.workspace.models.basket_variable import BasketVariable

# VIEWS


class BasketViewSet(  # pylint: disable=too-many-ancestors
    viewsets.ModelViewSet, CreateModelMixin, DestroyModelMixin
):
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

    def has_permission(self, request, _):
        if request.user.is_superuser:
            return True
        if request.method == "POST":
            if "basket" in request.data:
                basket = Basket.objects.get(id=request.data["basket"])
                return basket.user == request.user
            return False
        return True

    def has_object_permission(self, request, _, obj):
        if request.user.is_superuser:
            return True
        return obj.basket.user == request.user


class BasketVariableSet(  # pylint: disable=too-many-ancestors
    viewsets.ModelViewSet, CreateModelMixin
):
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


class EmailThrottle(AnonRateThrottle):  # pylint: disable=too-many-ancestors
    """Sets custom throttling rate through the settings."""

    scope = "sendmail"


class SendFeedback(APIView):
    """Process feedback form content to send feedback mails."""

    throttle_classes = [EmailThrottle]

    def get_permissions(self):
        """Allow feedback by anonymous users."""
        if self.request.method == "POST":
            return []
        return super().get_permissions()

    @staticmethod
    def get_queryset() -> QuerySet[Model]:
        """ApiView needs a queryset so we return an empty one here."""
        return Variable.objects.none()

    def post(self, request: Request) -> HttpResponseRedirect:
        """Process posted form data."""
        feedback_type = request.query_params.get("type", "")
        if not feedback_type:
            raise Http404

        form_data = request.data
        if "anon-submit-button" in form_data:
            email = "Anonymous"
        else:
            email = form_data["email"]

        feedback = form_data["feedback"]

        if form_data["source"]:
            source = form_data["source"]
        else:
            source = "No source url was given"

        message = (
            f"Feedback was sent from {email} \n\n"
            f"User entered feedback from: {source}\n\n"
            f"Feedback text:\n{feedback}"
        )

        to_email = FEEDBACK_TO_EMAILS.get(feedback_type, DEFAULT_FEEDBACK_TO_EMAIL)

        send_mail(
            f"Paneldata {type} Feedback: {form_data['feedback-type']}",
            message,
            None,
            [to_email],
            fail_silently=True,
        )
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class UserViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """List user metadata for admin users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
