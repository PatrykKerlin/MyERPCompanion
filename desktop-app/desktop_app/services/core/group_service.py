from schemas.core import GroupPlainSchema
from services.base import BaseViewService


class GroupService(BaseViewService[GroupPlainSchema]):
    _input_schema_cls = GroupPlainSchema
