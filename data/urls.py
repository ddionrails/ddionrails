from django.conf.urls import url

from data.views import (
    dataset_detail,
    variable_detail,
    variable_json,
    VariableDetailView
)

app_name = 'data'

urlpatterns = [
    url(
        r'^(?P<dataset_name>[a-z0-9_\-]+)$',
        dataset_detail,
        name="dataset",
    ),
    url(
        r'^(?P<dataset_name>[a-z0-9_\-]+)/(?P<variable_name>[a-z0-9_\-]+)$',
        VariableDetailView.as_view(),
        name="variable",
    ),
    url(
        r'^(?P<dataset_name>[a-z0-9_\-]+)/(?P<variable_name>[a-z0-9_\-]+).json$',
        variable_json,
        name="variable_json",
    ),
]
