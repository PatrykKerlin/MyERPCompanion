from .base_serializer import BaseSerializer
from ..models import Employee


class EmployeeListSerializer(BaseSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'middle_name', 'last_name']
        read_only_fields = ['employee_id']


class EmployeeDetailSerializer(EmployeeListSerializer):
    class Meta(EmployeeListSerializer.Meta):
        fields = (EmployeeListSerializer.Meta.fields +
                  ['identity_document', 'identity_document_number', 'pesel', 'date_of_birth', 'phone_country_code',
                   'phone_number', 'email', 'street', 'house_number', 'apartment_number', 'postal_code', 'city',
                   'country', 'bank_country_code', 'bank_account_number', 'bank_name', 'bank_swift',
                   'date_of_employment', 'position', 'department', 'salary'])
