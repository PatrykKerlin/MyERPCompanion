from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import PageLabels


@admin.register(PageLabels)
class PageLabelsAdmin(BaseAdmin):
    list_display = ['page', 'label']
