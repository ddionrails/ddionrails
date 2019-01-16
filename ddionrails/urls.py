from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

import instruments.views as instruments_views
import publications.views as publications_views
import studies.views as studies_views
from data.views import DatasetRedirectView, VariableRedirectView
from elastic.views import angular as angular_search
from studies.views import StudyDetailView, study_topics, study_topics2

from .views import (
    HomePageView,
    contact_page,
    elastic_proxy,
    elastic_test,
    imprint_page,
    quick_page,
)

handler400 = "ddionrails.views.bad_request"
handler403 = "ddionrails.views.permission_denied"
handler404 = "ddionrails.views.page_not_found"
handler500 = "ddionrails.views.server_error"

urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path("imprint/", imprint_page, name="imprint"),
    path("contact/", contact_page, name="contact"),
    path("quick/", quick_page, name="quickpage"),
    path("e_test/", elastic_test, name="elastic_test"),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("concept/", include("concepts.urls", namespace="concepts")),
    path("workspace/", include("workspace.urls", namespace="workspace")),
    path("search/", angular_search),
    path("search/", include("elastic.urls", namespace="elastic")),
    path("api/", include("api.urls", namespace="api")),
    path("django-rq/", include("django_rq.urls")),
    path("user/", include("django.contrib.auth.urls")),
    path("accounts/login/", LoginView.as_view()),
    path("elastic<path:path>", elastic_proxy),
    # Study by name
    path("<slug:study_name>", StudyDetailView.as_view(), name="study_detail"),
    # Study-specific links
    path("<slug:study_name>/data/", include("data.urls", namespace="data")),
    path("<slug:study_name>/publ/", include("publications.urls", namespace="publ")),
    path("<slug:study_name>/inst/", include("instruments.urls", namespace="inst")),
    path("<slug:study_name>/topics/<slug:language>", study_topics, name="study.topics"),
    path("<slug:study_name>/topics2/<slug:language>", study_topics2, name="study.topics"),
    # Redirects for search interface
    path("publication/<int:id>", publications_views.PublicationRedirectView.as_view()),
    path("variable/<int:id>", VariableRedirectView.as_view()),
    path("dataset/<int:id>", DatasetRedirectView.as_view()),
    path(
        "instrument/<int:id>",
        instruments_views.InstrumentRedirectView.as_view(),
        name="instrument_redirect",
    ),
    path(
        "question/<int:id>",
        instruments_views.QuestionRedirectView.as_view(),
        name="question_redirect",
    ),
    path("study/<int:id>", studies_views.StudyRedirectView.as_view()),
]


if settings.DEBUG and ("_hewing" or "_production") not in settings.WSGI_APPLICATION:
    import debug_toolbar
    urlpatterns = [path(r"__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
