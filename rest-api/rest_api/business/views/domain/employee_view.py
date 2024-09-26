from core.views.base.base_view import BaseView
from ...models import Employee
from ...serializers.domain.employee_serializer import EmployeeSerializer


class EmployeeView(BaseView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
