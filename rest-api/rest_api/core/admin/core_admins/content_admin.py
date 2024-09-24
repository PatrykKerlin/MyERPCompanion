from django.contrib import admin

from ..abstract_admins.base_admin import BaseAdmin
from ...models import Content


@admin.register(Content)
class ContentAdmin(BaseAdmin):
    list_display = ['page', 'name']
