from schemas.core import GroupPlainSchema
from services.base.base_view_service import BaseViewService


class GroupService(BaseViewService[GroupPlainSchema]):
    _input_schema_cls = GroupPlainSchema
