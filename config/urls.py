# -*- coding: utf-8 -*-

""" Root URLConf for ddionrails project """

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic.base import TemplateView

import ddionrails.instruments.views as instruments_views
import ddionrails.publications.views as publications_views
from config.views import HomePageView
from ddionrails.data.views import DatasetRedirectView, VariableRedirectView
from ddionrails.elastic.views import angular as angular_search
from ddionrails.studies.views import StudyDetailView, StudyRedirectView, study_topics

# These variable names are desired by Django
handler400 = "config.views.bad_request"  # pylint: disable=invalid-name
handler403 = "config.views.permission_denied"  # pylint: disable=invalid-name
handler404 = "config.views.page_not_found"  # pylint: disable=invalid-name
handler500 = "config.views.server_error"  # pylint: disable=invalid-name

admin.site.site_header = "DDI on Rails Admin"
admin.site.site_title = "DDI on Rails Admin"
admin.site.index_title = "Welcome to DDI on Rails Admin"

urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path(
        "imprint/",
        TemplateView.as_view(template_name="pages/imprint.html"),
        name="imprint",
    ),
    path(
        "contact/",
        TemplateView.as_view(template_name="pages/contact.html"),
        name="contact",
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("concept/", include("ddionrails.concepts.urls", namespace="concepts")),
    path("workspace/", include("ddionrails.workspace.urls", namespace="workspace")),
    path("search/", angular_search),
    path("api/", include("ddionrails.api.urls", namespace="api")),
    path("django-rq/", include("django_rq.urls")),
    path("user/", include("django.contrib.auth.urls")),
    path("accounts/login/", LoginView.as_view()),
    # Study by name
    path("<slug:study_name>", StudyDetailView.as_view(), name="study_detail"),
    # Study-specific links
    path("<slug:study_name>/data/", include("ddionrails.data.urls", namespace="data")),
    path(
        "<slug:study_name>/publ/",
        include("ddionrails.publications.urls", namespace="publ"),
    ),
    path(
        "<slug:study_name>/inst/",
        include("ddionrails.instruments.urls", namespace="inst"),
    ),
    path("<slug:study_name>/topics/<slug:language>", study_topics, name="study.topics"),
    # Redirects for search interface
    path(
        "publication/<uuid:id>",
        publications_views.PublicationRedirectView.as_view(),
        name="publication_redirect",
    ),
    path("variable/<uuid:id>", VariableRedirectView.as_view(), name="variable_redirect"),
    path("dataset/<uuid:id>", DatasetRedirectView.as_view(), name="dataset_redirect"),
    path(
        "instrument/<uuid:id>",
        instruments_views.InstrumentRedirectView.as_view(),
        name="instrument_redirect",
    ),
    path(
        "question/<uuid:id>",
        instruments_views.QuestionRedirectView.as_view(),
        name="question_redirect",
    ),
    path("study/<uuid:id>", StudyRedirectView.as_view()),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns = [path(r"__debug__/", include(debug_toolbar.urls))] + urlpatterns
