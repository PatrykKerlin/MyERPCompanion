from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .base_view import BaseView
from ..models import Employee
from ..serializers.employee_serializers import *


class EmployeeViews(BaseView):
    serializer_class = EmployeeDetailSerializer
    queryset = Employee.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateSerializer

        return self.serializer_class
