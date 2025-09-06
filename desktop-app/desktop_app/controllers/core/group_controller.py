from __future__ import annotations

from typing import Any

from controllers.base import BaseViewController
from schemas.core import GroupPlainSchema, GroupStrictSchema
from services.core import GroupService
from config.enums import ViewMode
from views.core import GroupView


class GroupController(BaseViewController[GroupService, GroupView, GroupPlainSchema, GroupStrictSchema]):
    _input_schema_cls = GroupPlainSchema
    _output_schema_cls = GroupStrictSchema
    _service_cls = GroupService

    def get_new_view(self, data_row: dict[str, Any] | None = None, mode: ViewMode = ViewMode.SEARCH) -> GroupView:
        self._view = GroupView(self, self._context.texts, 1, data_row, mode)
        return self._view
