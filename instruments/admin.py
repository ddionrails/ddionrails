from django.contrib import admin

from .models import Instrument, Question


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", "study", "period", "analysis_unit")
    list_filter = ("study", "period", "analysis_unit")
    list_per_page = 25
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "instrument")
    list_filter = ("instrument",)
    list_per_page = 25
    search_fields = ("name", "label")
