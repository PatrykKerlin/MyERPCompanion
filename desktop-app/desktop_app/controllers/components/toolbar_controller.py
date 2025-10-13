from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import TabsState
from utils.enums import ViewMode
from views.components.toolbar_component import ToolbarComponent
from events.events import RecordDeleteRequested, ToolbarRequested, SideMenuToggleRequested


if TYPE_CHECKING:
    from config.context import Context


class ToolbarController(BaseComponentController[ToolbarComponent, ToolbarRequested]):
    def __init__(self, context: Context):
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                ToolbarRequested: self._component_requested_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "tabs": self.__tabs_updated_listener,
            }
        )

    async def _component_requested_handler(self, _: ToolbarRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = ToolbarComponent(controller=self, translation=translation_state.items)
        self._state_store.update(components={"toolbar": self._component})

    def on_toggle_menu_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, SideMenuToggleRequested())

    def on_lock_view_clicked(self) -> None:
        if not self._component:
            return
        tabs_state = self._state_store.app_state.tabs
        if tabs_state.mode == ViewMode.SEARCH:
            self._state_store.update(tabs={"mode": ViewMode.CREATE})
        elif tabs_state.mode == ViewMode.READ:
            self._state_store.update(tabs={"mode": ViewMode.EDIT})
        self._component.set_lock_view_button_icon(unlocked=True)
        self._component.set_lock_view_button_state(disabled=True)

    def on_delete_clicked(self) -> None:
        if not self._component:
            return
        tabs_state = self._state_store.app_state.tabs
        data_row = tabs_state.items[tabs_state.current].data_row
        if not data_row or tabs_state.mode != ViewMode.READ:
            return
        row_id = data_row["id"]
        self._page.run_task(
            self._event_bus.publish,
            RecordDeleteRequested(key=tabs_state.items[tabs_state.current].view_key, id=row_id),
        )

    def __tabs_updated_listener(self, state: TabsState) -> None:
        if not self._component:
            return
        if state.mode == ViewMode.SEARCH and not state.items:
            self._component.set_lock_view_button_icon(unlocked=False)
            self._component.set_lock_view_button_state(disabled=True)
            self._component.set_delete_button_state(disabled=True)
        elif state.mode == ViewMode.SEARCH:
            self._component.set_lock_view_button_icon(unlocked=False)
            self._component.set_lock_view_button_state(disabled=False)
            self._component.set_delete_button_state(disabled=True)
        elif state.mode == ViewMode.LIST:
            self._component.set_lock_view_button_icon(unlocked=False)
            self._component.set_lock_view_button_state(disabled=True)
            self._component.set_delete_button_state(disabled=True)
        elif state.mode == ViewMode.READ:
            self._component.set_lock_view_button_icon(unlocked=False)
            self._component.set_lock_view_button_state(disabled=False)
            self._component.set_delete_button_state(disabled=False)
        elif state.mode == ViewMode.CREATE:
            self._component.set_lock_view_button_icon(unlocked=True)
            self._component.set_lock_view_button_state(disabled=False)
            self._component.set_delete_button_state(disabled=True)
        elif state.mode == ViewMode.EDIT:
            self._component.set_lock_view_button_icon(unlocked=True)
            self._component.set_lock_view_button_state(disabled=False)
            self._component.set_delete_button_state(disabled=True)

    # def refresh(self) -> None:
    #     self.__set_lock_view_button()
    #     self.__set_delete_record_button()

    # def __set_lock_view_button(self) -> None:
    #     active_view = self.__get_active_view()
    #     if not self.__toolbar or not active_view:
    #         return
    #     self.__toolbar.set_lock_view_button_icon(unlocked=False)
    #     if active_view.mode in (ViewMode.SEARCH, ViewMode.READ):
    #         self.__toolbar.set_lock_view_button_disabled(disabled=False)
    #     else:
    #         self.__toolbar.set_lock_view_button_disabled(disabled=True)

    # def __set_delete_record_button(self) -> None:
    #     active_view = self.__get_active_view()
    #     if not self.__toolbar or not active_view:
    #         return
    #     if active_view.mode == ViewMode.READ:
    #         self.__toolbar.set_delete_record_button_disabled(disabled=False)
    #     else:
    #         self.__toolbar.set_delete_record_button_disabled(disabled=True)

    # def __get_active_view(self) -> BaseView | None:
    #     active_view_key = self._context.controllers.get("tabs_bar").active_view_key
    #     return self._context.active_views.get(active_view_key, None)
