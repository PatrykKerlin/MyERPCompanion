from models.business import Department, Position
from schemas.business import DepartmentPlainSchema, DepartmentStrictSchema, PositionPlainSchema, PositionStrictSchema
from services.business import DepartmentService, PositionService
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

__all__ = [
    "DepartmentController",
    "EmployeeController",
    "PositionController",
]
