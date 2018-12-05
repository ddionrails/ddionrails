from django.contrib import admin

from .models import Basket


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    fields = ("name", "label", "description", "security_token", "user")
