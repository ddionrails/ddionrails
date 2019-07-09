# -*- coding: utf-8 -*-

""" URLConf for ddionrails.workspace app """

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import path

from .views import (
    account_overview,
    add_concept,
    add_variable,
    basket_delete,
    basket_detail,
    basket_list,
    basket_new,
    basket_search,
    basket_to_csv,
    register,
    remove_concept,
    remove_variable,
    script_delete,
    script_detail,
    script_new,
    script_new_lang,
    script_raw,
    user_delete,
)

app_name = "workspace"

urlpatterns = [
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), {"next_page": "/"}),
    path("register/", register, name="register"),
    path("delete_account/", user_delete, name="user_delete"),
    path("password_reset/", PasswordResetView.as_view()),
    path("account/", account_overview, name="account_overview"),
    path("baskets/", basket_list, name="basket_list"),
    path("baskets/new", basket_new, name="basket_list"),
    path("baskets/<int:basket_id>/csv", basket_to_csv, name="basket_to_csv"),
    path("baskets/<int:basket_id>/search", basket_search, name="basket_search"),
    path("baskets/<int:basket_id>/delete", basket_delete, name="basket_delete"),
    path(
        "baskets/<int:basket_id>/add/<uuid:variable_id>/",
        add_variable,
        name="add_variable",
    ),
    path(
        "baskets/<int:basket_id>/remove/<uuid:variable_id>/",
        remove_variable,
        name="remove_variable",
    ),
    path(
        "baskets/<int:basket_id>/add_concept/<uuid:concept_id>/",
        add_concept,
        name="add_concept",
    ),
    path(
        "baskets/<int:basket_id>/remove_concept/<uuid:concept_id>/",
        remove_concept,
        name="remove_concept",
    ),
    path("baskets/<int:basket_id>", basket_detail, name="basket_detail"),
    path("baskets/<int:basket_id>/scripts/new/<slug:generator_name>", script_new_lang),
    path("baskets/<int:basket_id>/scripts/new", script_new),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>/delete",
        script_delete,
        name="script_delete",
    ),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>",
        script_detail,
        name="script_detail",
    ),
    path(
        "baskets/<int:basket_id>/scripts/<int:script_id>/raw",
        script_raw,
        name="script_raw",
    ),
]
