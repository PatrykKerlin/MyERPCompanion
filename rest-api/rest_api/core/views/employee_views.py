from .base_view import BaseView
from ..models import Employee
from ..serializers.employee_serializers import *


class EmployeeViews(BaseView):
    queryset = Employee.objects.all()

    def get_serializer_class(self, serializers=None):
        serializers = {
            'list': EmployeeListSerializer,
            'retrieve': EmployeeDetailSerializer,
            ('create', 'update', 'partial_update'): EmployeeCreateSerializer,
        }

        return super().get_serializer_class(serializers=serializers)
