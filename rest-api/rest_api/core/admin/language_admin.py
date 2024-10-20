from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Language


@admin.register(Language)
class LanguageAdmin(BaseAdmin):
    list_display = ['name', 'value']
