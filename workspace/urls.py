from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

from .views import *

app_name = "workspace"

urlpatterns = [
    url(r"^login/$", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    url(r"^logout/$", LogoutView.as_view(), {"next_page": "/"}),
    url(r'^register/$', register, name="register"),
    url(r'^delete_account/$', user_delete),
    url(r'^password_reset/$', PasswordResetView.as_view()),
    url(r'^account/$', account_overview, name="account_overview"),
    url(r'^baskets/$', basket_list, name="basket_list"),
    url(r'^baskets/new$', basket_new, name="basket_list"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/csv$', basket_to_csv),
    url(r'^baskets/(?P<basket_id>[0-9]+)/search$', basket_search),
    url(r'^baskets/(?P<basket_id>[0-9]+)/delete$', basket_delete),
    url(r'^baskets/(?P<basket_id>[0-9]+)/add/(?P<variable_id>[0-9]+)/$',
        add_variable, name="add_variable"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/remove/(?P<variable_id>[0-9]+)/$',
        remove_variable, name="remove_variable"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/add_concept/(?P<concept_id>[0-9]+)/$',
        add_concept, name="add_concept"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/remove_concept/(?P<concept_id>[0-9]+)/$',
        remove_concept, name="remove_concept"),
    url(r'^baskets/(?P<basket_id>[0-9]+)$', basket_detail, name="basket"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/scripts/new/(?P<generator_name>[0-9a-z_-]+)$', script_new_lang),
    url(r'^baskets/(?P<basket_id>[0-9]+)/scripts/new$', script_new),
    url(r'^baskets/(?P<basket_id>[0-9]+)/scripts/(?P<script_id>[0-9]+)/delete$', script_delete),
    url(r'^baskets/(?P<basket_id>[0-9]+)/scripts/(?P<script_id>[0-9]+)$',
        script_detail, name="script_detail"),
    url(r'^baskets/(?P<basket_id>[0-9]+)/scripts/(?P<script_id>[0-9]+)/raw$',
        script_raw),
]
