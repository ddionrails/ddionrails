from django.conf.urls import url

from .views import PublicationDetailView, study_publication_list

app_name = "publications"

urlpatterns = [
    url(r"^$", study_publication_list, name="study_publication_list"),
    url(
        r"^(?P<publication_name>[a-z0-9_\-]+)",
        PublicationDetailView.as_view(),
        name="publication",
    ),
]
