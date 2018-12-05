from django.conf.urls import url

from .views import search

app_name = "elastic"

urlpatterns = [url(r"^$", search, name="search")]
