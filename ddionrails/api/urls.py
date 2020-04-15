# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from ddionrails.api.views import (
    BasketVariableSet,
    BasketViewSet,
    StudyViewSet,
    UserViewSet,
    VariableViewSet,
)
from ddionrails.instruments.views import question_comparison_partial

from . import views

app_name = "api"

urlpatterns = [
    path(
        "topics/<str:study_name>/baskets",
        views.baskets_by_study_and_user,
        name="baskets_by_study_and_user",
    ),
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
]

ROUTER = routers.SimpleRouter()
ROUTER.register(r"users", UserViewSet, basename="user")
ROUTER.register(r"baskets", BasketViewSet, basename="basket")
ROUTER.register(r"studies", StudyViewSet, basename="study")
ROUTER.register(r"variables", VariableViewSet)
ROUTER.register(r"basket-variables", BasketVariableSet, basename="basket-variables")

urlpatterns.append(re_path("^", include(ROUTER.urls)))
