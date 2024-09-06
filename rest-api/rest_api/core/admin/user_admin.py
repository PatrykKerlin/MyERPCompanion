from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from ..models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['username']
    fieldsets = [
        ['Credentials', {'fields': ['username', 'password']}],
        ['Details', {'fields': ['last_login', 'created_by', 'created_at', 'modified_by', 'modified_at', 'is_active']}],
    ]
    readonly_fields = ['last_login', 'created_by', 'created_at', 'modified_by', 'modified_at', 'is_active']

    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': ['username', 'password1', 'password2']
        }]
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['username']
        return self.readonly_fields
