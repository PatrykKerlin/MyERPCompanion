from django.contrib import admin
from ..models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['first_name', 'last_name', 'email', 'position', 'department']

    fieldsets = [
        ['Personal Information', {'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'pesel']}],
        ['Contact Information', {'fields': ['phone_country_code', 'phone_number', 'email']}],
        ['Address', {'fields': ['street', 'house_number', 'apartment_number', 'postal_code', 'city', 'country']}],
        ['Employment Details', {'fields': ['date_of_employment', 'position', 'department', 'salary']}],
        ['Bank Information', {'fields': ['bank_country_code', 'bank_account_number', 'bank_name', 'bank_swift']}],
        ['Identity Document', {'fields': ['identity_document']}],
        ['Additional Information', {'fields': ['created_by', 'created_at', 'modified_by', 'modified_at', 'is_active']}],
    ]

    readonly_fields = ['created_by', 'created_at', 'modified_by', 'modified_at', 'is_active']

    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': ['first_name', 'middle_name', 'last_name', 'email', 'position', 'department', 'phone_number',
                       'identity_document']
        }]
    ]
