from django.contrib import admin

from .models import Dataset, Variable


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "get_study_name", "period", "analysis_unit")
    list_filter = ("study__name", "period__name", "analysis_unit__name")
    list_per_page = 25
    search_fields = ("name",)
    list_select_related = ("study", "period", "analysis_unit")

    def get_study_name(self, obj):
        return obj.study.name

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "get_dataset_name", "get_study_name")
    list_filter = ("dataset__study__name",)
    list_per_page = 25
    search_fields = ("name", "label")
    list_select_related = ("dataset", "dataset__study")

    def get_dataset_name(self, obj):
        return obj.dataset.name

    get_dataset_name.admin_order_field = "dataset"
    get_dataset_name.short_description = "dataset"

    def get_study_name(self, obj):
        return obj.dataset.study.name

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"
