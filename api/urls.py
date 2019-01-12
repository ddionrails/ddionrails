from django.urls import path

from data.views import variable_preview_id

from .views import test_preview, test_redirect, test_rq

app_name = "api"

urlpatterns = [
    path("test/rq", test_rq, name="test_rq"),
    path(
        "test/preview/variable/<int:variable_id>",
        variable_preview_id,
        name="variable_preview",
    ),
    path(
        "test/preview/<str:object_type>/<int:object_id>",
        test_preview,
        name="test_preview",
    ),
    path(
        "test/redirect/<str:object_type>/<int:object_id>",
        test_redirect,
        name="test_redirect",
    ),
]
