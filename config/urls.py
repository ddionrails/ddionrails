# -*- coding: utf-8 -*-

""" Root URLConf for ddionrails project """

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.urls import include, path, re_path, register_converter
from django.views.generic.base import TemplateView

import ddionrails.instruments.views as instruments_views
import ddionrails.publications.views as publications_views
from config.views import HomePageView
from ddionrails.base.views import imprint
from ddionrails.concepts.views import TopicRedirectView
from ddionrails.data.views import DatasetRedirectView, VariableRedirectView
from ddionrails.instruments.views import QuestionRedirectView
from ddionrails.studies.models import Study
from ddionrails.studies.views import StudyDetailView, study_topics

# These variable names are desired by Django
handler400 = "config.views.bad_request"  # pylint: disable=invalid-name
handler403 = "config.views.permission_denied"  # pylint: disable=invalid-name
handler404 = "config.views.page_not_found"  # pylint: disable=invalid-name
handler500 = "config.views.server_error"  # pylint: disable=invalid-name

admin.site.site_header = "DDI on Rails Admin"
admin.site.site_title = "DDI on Rails Admin"
admin.site.index_title = "Welcome to DDI on Rails Admin"


class StudyConverter:
    """Get study object from url component."""

    regex = ".*"

    @staticmethod
    def to_python(value):
        """Get object"""
        return get_object_or_404(Study, name=value)

    @staticmethod
    def to_url(value):
        """Return string unchanged"""
        return value


register_converter(StudyConverter, "study")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("imprint/", imprint, name="imprint"),
    path(
        "contact/",
        TemplateView.as_view(template_name="pages/contact.html"),
        name="contact",
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("concept/", include("ddionrails.concepts.urls", namespace="concepts")),
    path("workspace/", include("ddionrails.workspace.urls", namespace="workspace")),
    re_path(
        (
            r"^search/"
            r"((?:all|variables|concepts|questions|publications|topics|statistics)"
            r"\?{0,1}.*){0,1}$"
        ),
        TemplateView.as_view(template_name="search/search.html"),
        name="search",
    ),
    path(
        "search/feedback/",
        TemplateView.as_view(template_name="search/feedback.html"),
        name="search_feedback",
    ),
    path("api/", include("ddionrails.api.urls", namespace="api")),
    path("django-rq/", include("django_rq.urls")),
    path("user/", include("django.contrib.auth.urls")),
    path(
        "<study:study>/statistics/",
        include("ddionrails.statistics.urls", namespace="statistics"),
        name="statistics",
    ),
    # Study by name
    path("<slug:study_name>/", StudyDetailView.as_view(), name="study_detail"),
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
    path("<slug:study_name>/topics/<slug:language>", study_topics, name="study_topics"),
    # Redirects for search interface
    path(
        "publication/<uuid:id>",
        publications_views.PublicationRedirectView.as_view(),
        name="publication_redirect",
    ),
    path("variable/<uuid:id>", VariableRedirectView.as_view(), name="variable_redirect"),
    path("dataset/<uuid:id>", DatasetRedirectView.as_view(), name="dataset_redirect"),
    path("topic/<uuid:id>", TopicRedirectView.as_view(), name="topic_redirect"),
    path(
        "instrument/<uuid:id>",
        instruments_views.InstrumentRedirectView.as_view(),
        name="instrument_redirect",
    ),
    path("question/<uuid:id>", QuestionRedirectView.as_view(), name="question_redirect"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns = [path(r"__debug__/", include(debug_toolbar.urls))] + urlpatterns


urlpatterns.append(
    path("auth/", include("rest_framework.urls", namespace="rest_framework"))
)
