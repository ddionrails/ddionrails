from django.contrib import admin

from .models import Basket


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "user", "study")
    list_filter = ("study",)
    list_per_page = 25
