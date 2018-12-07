from django.urls import path

from data.views import dataset_detail, variable_json, VariableDetailView

app_name = "data"

urlpatterns = [
    path("<slug:dataset_name>", dataset_detail, name="dataset"),
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
