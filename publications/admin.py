from django.contrib import admin

from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "author", "study", "period")
    list_per_page = 25
    search_fields = ("name", "title", "author")
