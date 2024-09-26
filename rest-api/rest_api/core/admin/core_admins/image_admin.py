from django.contrib import admin

from ..abstract_admins.base_admin import BaseAdmin
from ...models import Image


@admin.register(Image)
class ImageAdmin(BaseAdmin):
    list_display = ['key']
