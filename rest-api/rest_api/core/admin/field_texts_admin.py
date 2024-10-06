from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import FieldTexts


@admin.register(FieldTexts)
class FieldTextsAdmin(BaseAdmin):
    list_display = ['field', 'text']
