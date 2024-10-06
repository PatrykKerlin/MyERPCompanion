from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import Category


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['name']
