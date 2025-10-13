from models.business import Department, Position, Employee, Currency
from repositories.business import DepartmentRepository, PositionRepository, EmployeeRepository, CurrencyRepository
from schemas.business import (
    DepartmentPlainSchema,
    DepartmentStrictSchema,
    EmployeePlainSchema,
    EmployeeStrictSchema,
    PositionPlainSchema,
    PositionStrictSchema,
    CurrencyPlainSchema,
    CurrencyStrictSchema,
)
from utils.factories import ServiceFactory


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
CurrencyService = ServiceFactory.create(
    model_cls=Currency,
    repository_cls=CurrencyRepository,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)


__all__ = [
    "DepartmentService",
    "EmployeeService",
    "PositionService",
    "CurrencyService",
]
