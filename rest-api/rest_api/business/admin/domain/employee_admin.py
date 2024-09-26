from django.contrib import admin

from core.admin.base.base_admin import BaseAdmin
from ...models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ['first_name', 'last_name', ]
