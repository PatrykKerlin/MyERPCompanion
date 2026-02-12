from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from controllers.base.base_component_controller import BaseComponentController
from events.events import (
    ApiStatusRequested,
    MenuBarReady,
    MenuBarRequested,
    SideMenuToggleRequested,
    TabCloseAllRequested,
    TabCloseOthersRequested,
    TabCloseRequested,
    TabsBarToggleRequested,
    TabSearchRequested,
    ToolbarToggleRequested,
    ViewRequested,
)
from utils.enums import ViewMode
from views.components.menu_bar_component import MenuBarComponent

if TYPE_CHECKING:
    from config.context import Context


class MenuBarController(BaseComponentController[MenuBarComponent, MenuBarRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers({MenuBarRequested: self._component_requested_handler})

    def on_new_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view.clear_inputs()
        self._state_store.update(view={"mode": ViewMode.CREATE})

    def on_open_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view.clear_inputs()
        self._state_store.update(view={"mode": ViewMode.SEARCH})

    def on_save_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view._controller.on_save_clicked()

    def on_close_tab_clicked(self) -> None:
        title = self._state_store.app_state.view.title
        if not title:
            return
        self._page.run_task(self._event_bus.publish, TabCloseRequested(title))

    def on_close_other_tabs_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, TabCloseOthersRequested())

    def on_close_all_tabs_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, TabCloseAllRequested())

    def on_find_tab_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, TabSearchRequested())

    def on_undo_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view._controller.on_undo_clicked()

    def on_redo_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view._controller.on_redo_clicked()

    def on_copy_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view._controller.on_copy_clicked()

    def on_paste_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        if not view_state.view:
            return
        view_state.view._controller.on_paste_clicked()

    def on_refresh_clicked(self) -> None:
        view_state = self._state_store.app_state.view
        current_view = view_state.view
        if not current_view:
            return
        data_row = current_view.data_row
        record_id = data_row.get("id") if data_row else None
        module_id = current_view._controller._module_id
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=module_id,
                view_key=current_view.view_key,
                record_id=record_id,
                data=data_row,
            ),
        )

    def on_toggle_side_menu_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, SideMenuToggleRequested())

    def on_toggle_toolbar_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, ToolbarToggleRequested())

    def on_toggle_tabs_bar_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, TabsBarToggleRequested())

    def on_about_clicked(self) -> None:
        self._open_message_dialog("about")

    def on_check_api_status_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, ApiStatusRequested())

    async def _component_requested_handler(self, _: MenuBarRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = MenuBarComponent(controller=self, translation=translation_state.items)
        await self._event_bus.publish(MenuBarReady(self._component))
        self._page.on_keyboard_event = self.__on_keyboard_event

    def __on_keyboard_event(self, event: ft.KeyboardEvent) -> None:
        ctrl = event.ctrl or event.meta
        if not ctrl:
            return
        key = event.key.lower()
        if key == "o" and event.shift:
            self.on_close_other_tabs_clicked()
        elif key == "n":
            self.on_new_clicked()
        elif key == "o":
            self.on_open_clicked()
        elif key == "s":
            self.on_save_clicked()
        elif key == "w" and event.shift:
            self.on_close_all_tabs_clicked()
        elif key == "w":
            self.on_close_tab_clicked()
        elif key == "f":
            self.on_find_tab_clicked()
        elif key == "r":
            self.on_refresh_clicked()
        elif key == "z" and event.shift:
            self.on_redo_clicked()
        elif key == "z":
            self.on_undo_clicked()
        elif key == "y":
            self.on_redo_clicked()
        elif key == "c":
            self.on_copy_clicked()
        elif key == "v":
            self.on_paste_clicked()
