from django.contrib import admin

from .models import Study


class StudyInline(admin.TabularInline):
    model = Study
    extra = 0
    fields = ["name", "label", "repo"]


admin.site.register(Study)
