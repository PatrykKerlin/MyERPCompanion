from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from services.base.base_service import BaseService


class EmployeeService(BaseService[EmployeePlainSchema, EmployeeStrictSchema]):
    _plain_schema_cls = EmployeePlainSchema
