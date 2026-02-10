from controllers.business.hr.employee_controller import EmployeeController
from models.business.hr.department import Department
from models.business.hr.position import Position
from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from services.business.hr import DepartmentService, PositionService
from utils.controller_factory import ControllerFactory

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
