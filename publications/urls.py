from django.urls import path

from .views import PublicationDetailView, study_publication_list, publication_detail

app_name = "publications"

urlpatterns = [
    path("", study_publication_list, name="study_publication_list"),
    path("<slug:publication_name>", publication_detail, name="publication"),
]
