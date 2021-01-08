# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from ddionrails.api.views import (
    BasketVariableSet,
    BasketViewSet,
    QuestionViewSet,
    StudyViewSet,
    TopicTreeViewSet,
    UserViewSet,
    VariableViewSet,
)
from ddionrails.instruments.views import question_comparison_partial

app_name = "api"

urlpatterns = [
    path(
        "questions/compare/<uuid:from_id>/<uuid:to_id>",
        question_comparison_partial,
        name="question_comparison_partial",
    )
]

ROUTER = routers.SimpleRouter()
ROUTER.register(r"users", UserViewSet, basename="user")
ROUTER.register(r"baskets", BasketViewSet, basename="basket")
ROUTER.register(r"studies", StudyViewSet, basename="study")
ROUTER.register(r"topic-tree", TopicTreeViewSet, basename="topic-tree")
ROUTER.register(r"variables", VariableViewSet, basename="variable")
ROUTER.register(r"questions", QuestionViewSet, basename="question")
ROUTER.register(r"basket-variables", BasketVariableSet, basename="basket-variables")

urlpatterns.append(re_path("^", include(ROUTER.urls)))
