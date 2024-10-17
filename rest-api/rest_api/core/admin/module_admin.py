from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Module


@admin.register(Module)
class ModuleAdmin(BaseAdmin):
    list_display = ['name']
