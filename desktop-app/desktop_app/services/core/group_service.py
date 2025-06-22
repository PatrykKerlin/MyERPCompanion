from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.core import GroupInputSchema
from services.base import BaseViewService

if TYPE_CHECKING:
    from config.context import Context


class GroupService(BaseViewService[GroupInputSchema]):
    _input_schema_cls = GroupInputSchema

    def __init__(self, context: Context, endpoint: str) -> None:
        super().__init__(context, endpoint)
