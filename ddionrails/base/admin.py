"""Admin views for one of the base models.

Other base models do not need to be editable via the admin view.
"""
from django.contrib import admin

from ddionrails.base.mixins import AdminMixin

from .models import News


@admin.register(News)
class NewsAdmin(AdminMixin, admin.ModelAdmin):
    """Configure admin view for the News model."""

    list_display = ("id", "date", "content")
