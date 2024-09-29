from django.contrib import admin

from ..base.base_admin import BaseAdmin
from ...models import Image


@admin.register(Image)
class ImageAdmin(BaseAdmin):
    list_display = ['name', 'value']
