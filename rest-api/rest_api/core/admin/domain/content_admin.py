from django.contrib import admin

from ..base.base_admin import BaseAdmin
from ...models import Content


@admin.register(Content)
class ContentAdmin(BaseAdmin):
    list_display = ['page', 'key']
