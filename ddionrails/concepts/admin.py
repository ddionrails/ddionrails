from django.contrib import admin

from .models import AnalysisUnit, Concept, ConceptualDataset, Period


@admin.register(AnalysisUnit)
class AnalysisUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "label")


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ("name", "label")


@admin.register(ConceptualDataset)
class ConceptualDatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "label")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "study")
    list_filter = ("study",)
    list_per_page = 25
    search_fields = ("name",)
