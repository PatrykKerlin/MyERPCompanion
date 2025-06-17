from __future__ import annotations
from typing import TYPE_CHECKING, Any

from controllers.base import BaseViewController
from services.core import GroupService
from views.core import GroupView
from schemas.core import GroupOutputSchema
from utils.view_modes import ViewMode


class GroupController(BaseViewController[GroupService, GroupView, GroupOutputSchema]):
    _output_schema_cls = GroupOutputSchema
    _service_cls = GroupService

    def view(self, data_row: dict[str, Any] | None = None, mode: ViewMode = ViewMode.SEARCH) -> GroupView:
        self._view = GroupView(self, self._context.texts, 1, data_row, mode)
        return self._view
