from django.contrib import admin

from ..abstract_admins.base_admin import BaseAdmin
from ...models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ['first_name', 'last_name', ]
