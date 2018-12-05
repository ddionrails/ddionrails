from django.conf.urls import url
from .views import *
from data.views import variable_preview_id

app_name = 'api'

urlpatterns = [
    url(r'^test/rq$', test_rq, name="test_rq"),
    url(r'^test/preview/variable/(?P<variable_id>[a-z0-9_\-]+)$',
        variable_preview_id, name="variable_preview"),
    url(r'^test/preview/(?P<object_type>[A-Za-z]+)/(?P<object_id>[a-z0-9_\-]+)$',
        test_preview, name="test_preview"),
    url(r'^test/redirect/(?P<object_type>[A-Za-z]+)/(?P<object_id>[a-z0-9_\-]+)$',
        test_redirect, name="test_redirect"),
]
