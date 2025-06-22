from schemas.core import GroupInputSchema
from services.base import BaseViewService


class GroupService(BaseViewService[GroupInputSchema]):
    _input_schema_cls = GroupInputSchema
