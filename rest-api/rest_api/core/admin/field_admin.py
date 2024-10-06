from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Field


@admin.register(Field)
class FieldAdmin(BaseAdmin):
    list_display = ['name']