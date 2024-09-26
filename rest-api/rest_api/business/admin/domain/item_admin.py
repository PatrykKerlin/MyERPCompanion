from django.contrib import admin

from core.admin.base.base_admin import BaseAdmin
from ...models import Item


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    list_display = ['name', 'index']
