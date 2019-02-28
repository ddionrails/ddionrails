from django.contrib import admin

from .models import Dataset, Variable


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "study", "period", "analysis_unit")
    list_filter = ("study", "period", "analysis_unit")
    list_per_page = 25
    search_fields = ("name",)


admin.site.register(Variable)
