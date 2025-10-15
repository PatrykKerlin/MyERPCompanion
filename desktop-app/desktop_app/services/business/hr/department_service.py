from typing import Any
from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from services.base.base_service import BaseService


class DepartmentService(BaseService[DepartmentPlainSchema, DepartmentStrictSchema]):
    _plain_schema_cls = DepartmentPlainSchema
