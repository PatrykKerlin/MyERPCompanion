from django.contrib import admin

from base.admin import BaseAdmin


class AdminRegistrar:
    @staticmethod
    def register(Model, list_display_fields):
        class NewAdmin(BaseAdmin):
            list_display = list_display_fields

        admin.site.register(Model, NewAdmin)
