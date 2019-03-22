from django.contrib import admin

from .models import AnalysisUnit, Concept, ConceptualDataset, Period


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "study")
    list_filter = ("study",)
    list_per_page = 25
    search_fields = ("name",)


admin.site.register(Concept)
admin.site.register(AnalysisUnit)
admin.site.register(ConceptualDataset)
