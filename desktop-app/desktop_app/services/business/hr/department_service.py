from schemas.business import DepartmentPlainSchema
from services.base.base_view_service import BaseViewService


class DepartmentService(BaseViewService[DepartmentPlainSchema]):
    _input_schema_cls = DepartmentPlainSchema
