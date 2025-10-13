from models.business import Department, Position, Currency
from schemas.business import (
    DepartmentPlainSchema,
    DepartmentStrictSchema,
    PositionPlainSchema,
    PositionStrictSchema,
    CurrencyPlainSchema,
    CurrencyStrictSchema,
)
from services.business import DepartmentService, PositionService, CurrencyService
from utils.factories import ControllerFactory

from .hr.employee_controller import EmployeeController

DepartmentController = ControllerFactory.create(
    model_cls=Department,
    service_cls=DepartmentService,
    input_schema_cls=DepartmentStrictSchema,
    output_schema_cls=DepartmentPlainSchema,
)
PositionController = ControllerFactory.create(
    model_cls=Position,
    service_cls=PositionService,
    input_schema_cls=PositionStrictSchema,
    output_schema_cls=PositionPlainSchema,
)
CurrencyController = ControllerFactory.create(
    model_cls=Currency,
    service_cls=CurrencyService,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)

__all__ = [
    "DepartmentController",
    "EmployeeController",
    "PositionController",
    "CurrencyController",
]
