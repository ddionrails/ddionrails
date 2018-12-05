from django.contrib import admin

from .models import Dataset, Variable

admin.site.register(Dataset)
admin.site.register(Variable)
