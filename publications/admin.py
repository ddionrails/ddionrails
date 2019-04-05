from django.contrib import admin

from .models import Publication, Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("study", "dataset", "variable", "instrument", "question")
    list_per_page = 25

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("study", "dataset", "variable", "instrument", "question")
        )
        return queryset


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "author", "study", "year")
    list_select_related = ("study",)
    list_per_page = 25
    search_fields = ("name", "title", "author")
