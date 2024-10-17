from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import LabelTranslations


@admin.register(LabelTranslations)
class LabelTranslationsAdmin(BaseAdmin):
    list_display = ['label', 'translation']
