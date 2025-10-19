from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from utils.service_factory import ServiceFactory

DepartmentService = ServiceFactory.create(
    name_prefix="Department",
    plain_schema_cls=DepartmentPlainSchema,
    strict_schema_cls=DepartmentStrictSchema,
)
EmployeeService = ServiceFactory.create(
    name_prefix="Employee",
    plain_schema_cls=EmployeePlainSchema,
    strict_schema_cls=EmployeeStrictSchema,
)
PositionService = ServiceFactory.create(
    name_prefix="Position",
    plain_schema_cls=PositionPlainSchema,
    strict_schema_cls=PositionStrictSchema,
)

__all__ = [
    "DepartmentService",
    "EmployeeService",
    "PositionService",
]
