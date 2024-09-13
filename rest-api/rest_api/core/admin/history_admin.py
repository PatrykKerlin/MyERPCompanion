from django.contrib import admin

from .base_admin import BaseAdmin
from ..models import History


@admin.register(History)
class HistoryAdmin(BaseAdmin):
    ordering = ['id']
    list_display = ['table_name', 'record_id', 'modification_type', 'modified_at']

    fieldsets = [
        ['Record details:', {'fields': ['table_name', 'record_id', 'modification_type', 'data']}],
        ['Additional Information', {'fields': BaseAdmin.readonly_fields}],
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
