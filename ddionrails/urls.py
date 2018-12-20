import data.views as data_views
import instruments.views as instruments_views
import publications.views as publications_views
import studies.views as studies_views
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LoginView
from elastic.views import angular as angular_search
from studies.views import StudyDetailView, study_topics, study_topics2

from .views import HomePageView, contact_page, elastic_proxy, elastic_test, imprint_page, quick_page

handler400 = "ddionrails.views.bad_request"
handler403 = "ddionrails.views.permission_denied"
handler404 = "ddionrails.views.page_not_found"
handler500 = "ddionrails.views.server_error"

urlpatterns = [
    url(r"^$", HomePageView.as_view(), name="homepage"),
    url(r"^imprint/$", imprint_page, name="imprint"),
    url(r"^contact/$", contact_page, name="contact"),
    url(r"^quick/$", quick_page, name="quickpage"),
    url(r"^e_test/$", elastic_test, name="elastic_test"),
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", admin.site.urls),
    url(r"^concept/", include("concepts.urls", namespace="concepts")),
    url(r"^workspace/", include("workspace.urls", namespace="workspace")),
    url(r"^search/$", angular_search),
    url(r"^search/", include("elastic.urls", namespace="elastic")),
    url(r"^api/", include("api.urls", namespace="api")),
    url(r"^django-rq/", include("django_rq.urls")),
    url(r"^user/", include("django.contrib.auth.urls")),
    url(r"^accounts/login/", LoginView.as_view()),
    url(r"^elastic(?P<path>.*)$", elastic_proxy),
    # Study by name
    url(r"^(?P<study_name>[a-z0-9_\-]+)$", StudyDetailView.as_view(), name="study_detail"),
    # Study-specific links
    url(r"^(?P<study_name>[a-z0-9_\-]+)/data/", include("data.urls", namespace="data")),
    url(r"^(?P<study_name>[a-z0-9_\-]+)/publ/", include("publications.urls", namespace="publ")),
    url(r"^(?P<study_name>[a-z0-9_\-]+)/inst/", include("instruments.urls", namespace="inst")),
    url(r"^(?P<study_name>[a-z0-9_\-]+)/topics/(?P<language>[a-z]+)", study_topics, name="study.topics"),
    url(r"^(?P<study_name>[a-z0-9_\-]+)/topics2/(?P<language>[a-z]+)", study_topics2, name="study.topics"),
    # Redirects for search interface
    url(r"^publication/(?P<id>[0-9]+)", publications_views.PublicationRedirectView.as_view()),
    url(r"^variable/(?P<id>[0-9]+)", data_views.variable_redirect),
    url(r"^dataset/(?P<id>[0-9]+)", data_views.dataset_redirect),
    url(r"^instrument/(?P<id>[0-9]+)", instruments_views.InstrumentRedirectView.as_view(), name="instrument_redirect"),
    url(r"^question/(?P<id>[0-9]+)", instruments_views.QuestionRedirectView.as_view(), name="question_redirect"),
    url(r"^study/(?P<id>[0-9]+)", studies_views.StudyRedirectView.as_view()),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += [url(r"^silk/", include("silk.urls", namespace="silk"))]
