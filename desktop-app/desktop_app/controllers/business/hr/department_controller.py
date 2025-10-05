from __future__ import annotations

from typing import Any

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business import DepartmentPlainSchema, DepartmentStrictSchema
from services.business.hr.department_service import DepartmentService
from utils.enums import ViewMode
from views.business.hr.department_view import DepartmentView
from events.view_events import DepartmentViewRequested, ViewReady


class DepartmentController(
    BaseViewController[DepartmentService, DepartmentView, DepartmentPlainSchema, DepartmentStrictSchema]
):
    _input_schema_cls = DepartmentPlainSchema
    _output_schema_cls = DepartmentStrictSchema
    _service_cls = DepartmentService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers({DepartmentViewRequested: self._view_requested_handler})

    async def _view_requested_handler(self, event: DepartmentViewRequested) -> None:
        translation_service = self._state_store.app_state.translation
        self._view = DepartmentView(self, translation_service.items)
        await self._event_bus.publish(ViewReady(key=event.key, view=self._view))
