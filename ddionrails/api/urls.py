# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.contrib.auth.models import User
from django.urls import path, re_path
from rest_framework import routers, viewsets

from ddionrails.api.serializers import (
    BasketSerializer,
    StudySerializer,
    UserSerializer,
    VariableSerializer,
)
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.views import question_comparison_partial
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket

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


class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Basket.objects.all()
        return Basket.objects.filter(user=user.id)


class BasketVariableSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Variable.objects.all()
        return Variable.objects.filter(basket__user=user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.id)


ROUTER = routers.SimpleRouter()
ROUTER.register(r"users", UserViewSet)
ROUTER.register(r"baskets", BasketViewSet)
ROUTER.register(r"studies", StudyViewSet)
ROUTER.register(r"variables", VariableViewSet)

urlpatterns.append(re_path("^", include(ROUTER.urls)))
