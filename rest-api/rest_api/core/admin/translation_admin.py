from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Translation


@admin.register(Translation)
class TranslationAdmin(BaseAdmin):
    list_display = ['language', 'value']
