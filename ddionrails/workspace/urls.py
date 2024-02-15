# -*- coding: utf-8 -*-

""" URLConf for ddionrails.workspace app """

from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import path

from . import views

app_name = "workspace"

urlpatterns = [
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("register/", views.register, name="register"),
    path("delete_account/", views.user_delete, name="user_delete"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("account/", views.account_overview, name="account_overview"),
    path("baskets/", views.basket_list, name="basket_list"),
    path("baskets/new", views.basket_new, name="basket_new"),
    path("baskets/<int:basket_id>/csv", views.basket_to_csv, name="basket_to_csv"),
    path("baskets/<int:basket_id>/search", views.basket_search, name="basket_search"),
    path("baskets/<int:basket_id>/delete", views.basket_delete, name="basket_delete"),
    path(
        "baskets/<int:basket_id>/add_concept/<uuid:concept_id>/",
        views.add_concept,
        name="add_concept",
    ),
    path(
        "baskets/<int:basket_id>/remove_concept/<uuid:concept_id>/",
        views.remove_concept,
        name="remove_concept",
    ),
    path("baskets/<int:basket_id>", views.basket_detail, name="basket_detail"),
    path(
        "baskets/<int:basket_id>/scripts/new/<slug:generator_name>",
        views.script_new_lang,
        name="script_new_lang",
    ),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>/delete",
        views.script_delete,
        name="script_delete",
    ),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>",
        views.script_detail,
        name="script_detail",
    ),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>/raw",
        views.script_raw,
        name="script_raw",
    ),
]
