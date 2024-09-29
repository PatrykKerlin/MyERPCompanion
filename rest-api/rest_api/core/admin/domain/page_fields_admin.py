from django.contrib import admin

from ..base.base_admin import BaseAdmin
from ...models import PageFields


@admin.register(PageFields)
class PageFieldsAdmin(BaseAdmin):
    list_display = ['page', 'field']
