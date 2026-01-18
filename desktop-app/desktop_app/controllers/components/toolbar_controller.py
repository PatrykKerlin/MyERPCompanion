from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import ViewState
from utils.enums import EditDisabledView, ViewMode
from views.components.toolbar_component import ToolbarComponent
from events.events import RecordDeleteRequested, ToolbarReady, ToolbarRequested, SideMenuToggleRequested


if TYPE_CHECKING:
    from config.context import Context


class ToolbarController(BaseComponentController[ToolbarComponent, ToolbarRequested]):
    def __init__(self, context: Context):
        super().__init__(context)
        self.__state_handlers = {
            ViewMode.NONE: self.__set_none_mode,
            ViewMode.SEARCH: self.__set_search_mode,
            ViewMode.LIST: self.__set_list_mode,
            ViewMode.READ: self.__set_read_mode,
            ViewMode.CREATE: self.__set_create_mode,
            ViewMode.EDIT: self.__set_edit_mode,
            ViewMode.STATIC: self.__set_static_mode,
        }
        self._subscribe_event_handlers(
            {
                ToolbarRequested: self._component_requested_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "view": self.__view_updated_listener,
            }
        )

    async def _component_requested_handler(self, _: ToolbarRequested) -> None:
        translation = self._state_store.app_state.translation.items
        self._component = ToolbarComponent(controller=self, translation=translation)
        await self._event_bus.publish(ToolbarReady(self._component))

    def on_toggle_menu_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, SideMenuToggleRequested())

    def on_lock_view_clicked(self) -> None:
        if not self._component:
            return
        view_state = self._state_store.app_state.view
        if view_state.mode == ViewMode.SEARCH:
            self._state_store.update(view={"mode": ViewMode.CREATE})
        elif view_state.mode == ViewMode.READ:
            if view_state.view and view_state.view.view_key.value in set(EditDisabledView):
                return
            self._state_store.update(view={"mode": ViewMode.EDIT})
        self._component.set_lock_view_button_icon(unlocked=True)
        self._component.set_lock_view_button_state(disabled=True)

    def on_delete_clicked(self) -> None:
        if not self._component:
            return
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        data_row = getattr(view_state.view, "data_row", None)
        if not data_row or view_state.mode != ViewMode.READ:
            return
        self._page.run_task(
            self._event_bus.publish,
            RecordDeleteRequested(view_key=view_state.view.view_key, id=data_row["id"]),
        )

    def __view_updated_listener(self, state: ViewState) -> None:
        self.__state_handlers[state.mode]()

    def __set_none_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=False)
        self._component.set_lock_view_button_state(disabled=True)
        self._component.set_delete_button_state(disabled=True)

    def __set_search_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=False)
        self._component.set_lock_view_button_state(disabled=False)
        self._component.set_delete_button_state(disabled=True)

    def __set_list_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=False)
        self._component.set_lock_view_button_state(disabled=True)
        self._component.set_delete_button_state(disabled=True)

    def __set_read_mode(self) -> None:
        if not self._component:
            return
        view_state = self._state_store.app_state.view
        if view_state.view and view_state.view.view_key.value in EditDisabledView._value2member_map_:
            self._component.set_lock_view_button_icon(unlocked=False)
            self._component.set_lock_view_button_state(disabled=True)
            self._component.set_delete_button_state(disabled=False)
            return
        self._component.set_lock_view_button_icon(unlocked=False)
        self._component.set_lock_view_button_state(disabled=False)
        self._component.set_delete_button_state(disabled=False)

    def __set_create_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=True)
        self._component.set_lock_view_button_state(disabled=False)
        self._component.set_delete_button_state(disabled=True)

    def __set_edit_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=True)
        self._component.set_lock_view_button_state(disabled=False)
        self._component.set_delete_button_state(disabled=True)

    def __set_static_mode(self) -> None:
        if not self._component:
            return
        self._component.set_lock_view_button_icon(unlocked=False)
        self._component.set_lock_view_button_state(disabled=True)
        self._component.set_delete_button_state(disabled=True)
