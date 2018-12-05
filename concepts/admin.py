from django.contrib import admin

from .models import (
    AnalysisUnit,
    Concept,
    ConceptualDataset,
    Period,
)

admin.site.register(Concept)
admin.site.register(AnalysisUnit)
admin.site.register(Period)
admin.site.register(ConceptualDataset)
