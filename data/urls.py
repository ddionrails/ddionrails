from django.urls import path

from data.views import DatasetDetailView, VariableDetailView, variable_json

app_name = "data"

urlpatterns = [
    path("<slug:dataset_name>", DatasetDetailView.as_view(), name="dataset"),
    path(
        "<slug:dataset_name>/<slug:variable_name>",
        VariableDetailView.as_view(),
        name="variable",
    ),
    path(
        "<slug:dataset_name>/<slug:variable_name>.json",
        variable_json,
        name="variable_json",
    ),
]
