from models.business.hr.department import Department
from models.business.hr.employee import Employee
from models.business.hr.position import Position
from repositories.business.hr import DepartmentRepository, PositionRepository
from repositories.business.hr.employee_repository import EmployeeRepository
from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from utils.service_factory import ServiceFactory

DepartmentService = ServiceFactory.create(
    model_cls=Department,
    repository_cls=DepartmentRepository,
    input_schema_cls=DepartmentStrictSchema,
    output_schema_cls=DepartmentPlainSchema,
)
PositionService = ServiceFactory.create(
    model_cls=Position,
    repository_cls=PositionRepository,
    input_schema_cls=PositionStrictSchema,
    output_schema_cls=PositionPlainSchema,
)
EmployeeService = ServiceFactory.create(
    model_cls=Employee,
    repository_cls=EmployeeRepository,
    input_schema_cls=EmployeeStrictSchema,
    output_schema_cls=EmployeePlainSchema,
)

__all__ = [
    "DepartmentService",
    "EmployeeService",
    "PositionService",
]
