from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .base_admin import BaseAdmin
from ..models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    ordering = ['id']
    list_display = ['login']
    readonly_fields = ['last_login'] + BaseAdmin.readonly_fields
    fieldsets = [
        ['Credentials', {'fields': ['employee', 'login', 'password']}],
        ['Additional Information', {'fields': BaseAdmin.readonly_fields}],
    ]
    list_filter = ("is_staff", "is_superuser", "groups")

    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': ['employee', 'password1', 'password2']
        }]
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['employee', 'login']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        BaseAdmin.save_model(self, request, obj, form, change)
