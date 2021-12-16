# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from ddionrails.api.views import (
    BasketVariableSet,
    BasketViewSet,
    QuestionComparisonViewSet,
    QuestionViewSet,
    StudyViewSet,
    TopicTreeViewSet,
    UserViewSet,
    VariableViewSet,
)

app_name = "api"

urlpatterns = []

ROUTER = routers.SimpleRouter()
ROUTER.register(r"users", UserViewSet, basename="user")
ROUTER.register(r"baskets", BasketViewSet, basename="basket")
ROUTER.register(r"studies", StudyViewSet, basename="study")
ROUTER.register(r"topic-tree", TopicTreeViewSet, basename="topic-tree")
ROUTER.register(r"variables", VariableViewSet, basename="variable")
ROUTER.register(r"questions", QuestionViewSet, basename="question")
ROUTER.register(
    r"question-comparison", QuestionComparisonViewSet, basename="question-comparison"
)
ROUTER.register(r"basket-variables", BasketVariableSet, basename="basket-variables")

urlpatterns.append(re_path("^", include(ROUTER.urls)))
