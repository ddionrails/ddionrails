# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """


from django.conf.urls import include
from django.urls import path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from ddionrails.api.views.datasets import (
    DatasetViewSet,
    VariableLabelsViewSet,
    VariableViewSet,
)
from ddionrails.api.views.instruments import (
    InstrumentViewSet,
    QuestionComparisonViewSet,
    QuestionViewSet,
)
from ddionrails.api.views.studies import StudyViewSet, TopicRootAndLeafs, TopicTreeViewSet
from ddionrails.api.views.user_tools import (
    BasketVariableSet,
    BasketViewSet,
    SendFeedback,
    UserViewSet,
)

app_name = "api"

urlpatterns = [
    path("feedback/", SendFeedback.as_view(), name="send-feedback"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url="/api/schema/"),
        name="swagger-ui",
    ),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

ROUTER = routers.SimpleRouter()
ROUTER.register(r"baskets", BasketViewSet, basename="basket")
ROUTER.register(r"basket-variables", BasketVariableSet, basename="basket-variables")
ROUTER.register(r"datasets", DatasetViewSet, basename="dataset")
ROUTER.register(r"instruments", InstrumentViewSet, basename="instrument")
ROUTER.register(r"questions", QuestionViewSet, basename="question")
ROUTER.register(
    r"question-comparison", QuestionComparisonViewSet, basename="question-comparison"
)
ROUTER.register(r"users", UserViewSet, basename="user")
ROUTER.register(r"studies", StudyViewSet, basename="study")
ROUTER.register(r"topic-tree", TopicTreeViewSet, basename="topic-tree")
ROUTER.register(r"topic-leafs", TopicRootAndLeafs, basename="topic-leafs")
ROUTER.register(r"variables", VariableViewSet, basename="variable")
ROUTER.register(r"variable_labels", VariableLabelsViewSet, basename="variable_labels")

urlpatterns.append(re_path("^", include(ROUTER.urls)))
