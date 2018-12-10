from django.urls import path


from .views import search

app_name = "elastic"

urlpatterns = [path("", search, name="search")]
