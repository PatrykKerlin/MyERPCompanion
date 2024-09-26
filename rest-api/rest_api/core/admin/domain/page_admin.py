from django.contrib import admin

from ..base.base_admin import BaseAdmin
from ...models import Page


@admin.register(Page)
class PageAdmin(BaseAdmin):
    list_display = ['title']