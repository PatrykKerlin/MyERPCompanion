from django.contrib import admin

from base.admin.base_admin import BaseAdmin
from ..models import PageImages


@admin.register(PageImages)
class PageImagesAdmin(BaseAdmin):
    list_display = ['page', 'image']
