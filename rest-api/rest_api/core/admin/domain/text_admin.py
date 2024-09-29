from django.contrib import admin

from ..base.base_admin import BaseAdmin
from ...models import Text


@admin.register(Text)
class TextAdmin(BaseAdmin):
    list_display = ['language', 'value']
