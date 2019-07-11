# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.urls import path

from ddionrails.instruments.views import question_comparison_partial

from . import views

app_name = "api"

urlpatterns = [
    path(
        "questions/compare/<uuid:from_id>/<uuid:to_id>",
        question_comparison_partial,
        name="question_comparison_partial",
    ),
    path(
        "test/redirect/<str:object_type>/<uuid:object_id>",
        views.object_redirect,
        name="object_redirect",
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
