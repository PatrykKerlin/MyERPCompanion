from django.contrib import admin

from .base_admin import BaseAdmin
from ..models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    ordering = ['id']
    list_display = ['first_name', 'last_name', 'email', 'position', 'department']

    fieldsets = [
        ['Personal Information',
         {'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'pesel']}],
        ['Contact Information', {'fields': ['phone_country_code', 'phone_number', 'email']}],
        ['Address', {'fields': ['street', 'house_number', 'apartment_number', 'postal_code', 'city', 'country']}],
        ['Employment Details', {'fields': ['date_of_employment', 'position', 'department', 'salary']}],
        ['Bank Information', {'fields': ['bank_country_code', 'bank_account_number', 'bank_name', 'bank_swift']}],
        ['Identity Document', {'fields': ['identity_document', 'identity_document_number']}],
        ['Additional Information', {'fields': BaseAdmin.readonly_fields}],
    ]
