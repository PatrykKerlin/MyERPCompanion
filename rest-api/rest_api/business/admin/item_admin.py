from django.contrib import admin

from base.admin import BaseAdmin
from ..models import Item


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    list_display = ['name', 'index']
