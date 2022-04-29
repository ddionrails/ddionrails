# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from ddionrails.api.views.datasets import (
    StatisticsMetadataViewSet,
    StatisticViewSet,
    VariableViewSet,
)
from ddionrails.api.views.instruments import (
    InstrumentViewSet,
    QuestionComparisonViewSet,
    QuestionViewSet,
)
from ddionrails.api.views.studies import StudyViewSet, TopicTreeViewSet
from ddionrails.api.views.user_tools import (
    BasketVariableSet,
    BasketViewSet,
    SendFeedback,
    UserViewSet,
)

app_name = "api"

urlpatterns = [path("feedback/", SendFeedback.as_view(), name="send-feedback")]

ROUTER = routers.SimpleRouter()
ROUTER.register(r"baskets", BasketViewSet, basename="basket")
ROUTER.register(r"basket-variables", BasketVariableSet, basename="basket-variables")
ROUTER.register(r"instruments", InstrumentViewSet, basename="instrument")
ROUTER.register(r"questions", QuestionViewSet, basename="question")
ROUTER.register(
    r"question-comparison", QuestionComparisonViewSet, basename="question-comparison"
)
ROUTER.register(r"users", UserViewSet, basename="user")
ROUTER.register(r"statistic", StatisticViewSet, basename="statistic")
ROUTER.register(
    r"statistics-metadata", StatisticsMetadataViewSet, basename="statistics-metadata"
)
ROUTER.register(r"studies", StudyViewSet, basename="study")
ROUTER.register(r"topic-tree", TopicTreeViewSet, basename="topic-tree")
ROUTER.register(r"variables", VariableViewSet, basename="variable")

urlpatterns.append(re_path("^", include(ROUTER.urls)))
