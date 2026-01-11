from __future__ import annotations

from typing import Any

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from services.core.group_service import GroupService
from utils.enums import ViewMode
from views.core.group_view import GroupView
from events.events import ViewRequested, ViewReady


class GroupController(BaseViewController[GroupService, GroupView, GroupPlainSchema, GroupStrictSchema]):
    _plain_schema_cls = GroupPlainSchema
    _strict_schema_cls = GroupStrictSchema
    _service_cls = GroupService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers({ViewRequested: self.__view_requested_handler})

    async def __view_requested_handler(self, event: ViewRequested) -> None:
        pass
        # translation_service = self._state_store.app_state.translation
        # self._view = GroupView(self, translation_service.items)
        # await self._event_bus.publish(ViewReady(key=event.key, view=self._view))
