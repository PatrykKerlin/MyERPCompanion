from .base_serializer import BaseSerializer
from ..models import Employee


class EmployeeListSerializer(BaseSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'middle_name', 'last_name']


class EmployeeCreateSerializer(EmployeeListSerializer):
    class Meta(EmployeeListSerializer.Meta):
        fields = BaseSerializer.get_model_specific_fields(EmployeeListSerializer.Meta.model)


class EmployeeDetailSerializer(EmployeeCreateSerializer):
    class Meta(EmployeeCreateSerializer.Meta):
        fields = EmployeeCreateSerializer.Meta.fields + BaseSerializer.get_model_common_fields()
