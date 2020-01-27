# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path, re_path
from rest_framework import generics, routers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ddionrails.api.serializers import (
    BasketHyperlinkedSerializer,
    BasketVariableSerializer,
    StudySerializer,
    UserSerializer,
    VariableSerializer,
)
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.views import question_comparison_partial
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable

from . import views

app_name = "api"

urlpatterns = [
    path(
        "questions/compare/<uuid:from_id>/<uuid:to_id>",
        question_comparison_partial,
        name="question_comparison_partial",
    ),
    path("topics/<str:study_name>/<str:language>", views.topic_list, name="topic_list"),
    path(
        "topics/<str:study_name>/<str:language>/concept_<str:concept_name>",
        views.concept_by_study,
        name="concept_by_study",
    ),
    path(
        "topics/<str:study_name>/<str:language>/topic_<str:topic_name>",
        views.topic_by_study,
        name="topic_by_study",
    ),
    path(
        "topics/<str:study_name>/<str:language>/baskets",
        views.baskets_by_study_and_user,
        name="baskets_by_study_and_user",
    ),
    path(
        "topics/<str:study_name>/<str:language>/concept_<str:concept_name>/add_to_basket/<int:basket_id>",
        views.add_variables_by_concept,
        name="add_variables_by_concept",
    ),
    path(
        "topics/<str:study_name>/<str:language>/topic_<str:topic_name>/add_to_basket/<int:basket_id>",
        views.add_variables_by_topic,
        name="add_variables_by_topic",
    ),
    path(
        "topics/<str:study_name>/<str:language>/variable_<uuid:variable_id>/add_to_basket/<int:basket_id>",
        views.add_variable_by_id,
        name="add_variable_by_id",
    ),
]


# pylint: disable=too-many-ancestors


class StudyViewSet(viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariableSerializer


class BasketViewSet(viewsets.ModelViewSet, CreateModelMixin):
    """List baskets or create one.
    
    Baskets are listed according to permissions.
    Normal users can only retrieve their owned baskets.
    Superusers can list all baskets.

    Basket creation is the same.
    Normal users can create baskets for themselves.
    Superusers can create baskets for arbitrary users. 
    """

    queryset = Basket.objects.all()
    serializer_class = BasketHyperlinkedSerializer

    def get_queryset(self):
        """get queryset according to permissions."""
        user = self.request.user
        if user.is_superuser:
            return Basket.objects.all()
        return Basket.objects.filter(user=user.id)

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

        serializer = BasketHyperlinkedSerializer(basket, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BasketVariableSet(viewsets.ModelViewSet):
    queryset = BasketVariable.objects.all()
    serializer_class = BasketVariableSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BasketVariable.objects.all()
        return BasketVariable.objects.filter(basket__user=user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


ROUTER = routers.SimpleRouter()
ROUTER.register(r"users", UserViewSet)
ROUTER.register(r"baskets", BasketViewSet)
ROUTER.register(r"studies", StudyViewSet)
ROUTER.register(r"variables", VariableViewSet)
ROUTER.register(r"basket-variables", BasketVariableSet)

urlpatterns.append(re_path("^", include(ROUTER.urls)))
