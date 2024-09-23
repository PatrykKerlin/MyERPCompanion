from .base_serializer import BaseSerializer
from ..models import Employee


class EmployeeSerializer(BaseSerializer):
    class Meta:
        model = Employee

    def _get_list_fields(self):
        return ['first_name', 'middle_name', 'last_name']
