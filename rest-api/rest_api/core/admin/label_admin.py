from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Label


@admin.register(Label)
class LabelAdmin(BaseAdmin):
    list_display = ['name']
