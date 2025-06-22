from __future__ import annotations

from typing import Any

from controllers.base import BaseViewController
from schemas.core import GroupOutputSchema
from services.core import GroupService
from utils.view_modes import ViewMode
from views.core import GroupView


class GroupController(BaseViewController[GroupService, GroupView, GroupOutputSchema]):
    _output_schema_cls = GroupOutputSchema
    _service_cls = GroupService

    def get_new_view(self, data_row: dict[str, Any] | None = None, mode: ViewMode = ViewMode.SEARCH) -> GroupView:
        self._view = GroupView(self, self._context.texts, 1, data_row, mode, self._endpoint.key)
        return self._view
