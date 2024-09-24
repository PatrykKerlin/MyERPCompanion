from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from ..abstract_admins.base_admin import BaseAdmin
from ...models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    ordering = ['id']
    list_display = ['login']

    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': ['employee', 'password1', 'password2']
        }]
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['last_login'] + super().get_readonly_fields(request, obj)

        if obj:
            readonly_fields += ['employee', 'login']

        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ['Credentials', {'fields': ['employee', 'login', 'password']}],
            ['Additional Information', {'fields': self.get_readonly_fields(request, obj)}],
        ]

        return fieldsets

    def save_model(self, request, obj, form, change):
        BaseAdmin.save_model(self, request, obj, form, change)
