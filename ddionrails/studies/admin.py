from django.contrib import admin

from .models import Study


class StudyInline(admin.TabularInline):
    model = Study
    extra = 0
    fields = ["name", "label", "repo"]


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "created", "modified")
