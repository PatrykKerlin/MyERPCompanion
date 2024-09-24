from django.contrib import admin

from ..abstract_admins.base_admin import BaseAdmin
from ...models import Item


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    list_display = ['name', 'index']
