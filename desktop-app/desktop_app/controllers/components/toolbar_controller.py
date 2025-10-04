from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from views.components.toolbar_component import ToolbarComponent
from events.events import ToolbarRequested, SideMenuToggleRequested

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

    async def _component_requested_handler(self, _: ToolbarRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = ToolbarComponent(controller=self, translation=translation_state.items)
        self._state_store.update(components={"toolbar": self._component})

    def on_toggle_menu_clicked(self) -> None:
        self._page.run_task(self._event_bus.publish, SideMenuToggleRequested())
        # side_menu = self._context.controllers.get("side_menu").side_menu
        # if not side_menu:
        #     return
        # if not self.__side_menu_width:
        #     self.__side_menu_width = side_menu.width
        # self.__side_menu_visible = not self.__side_menu_visible
        # side_menu.width = self.__side_menu_width if self.__side_menu_visible else 0
        # side_menu.opacity = 1.0 if self.__side_menu_visible else 0.0
        # self._page.update()

    # def on_lock_view_clicked(self) -> None:
    #     active_view = self.__get_active_view()
    #     if not self.__toolbar or not active_view:
    #         return
    #     self.__toolbar.set_lock_view_button_icon(unlocked=True)
    #     self.__toolbar.set_lock_view_button_disabled(disabled=True)
    #     if active_view.mode == ViewMode.SEARCH:
    #         active_view.set_create_mode()
    #     elif active_view.mode == ViewMode.READ:
    #         active_view.set_edit_mode()

    # def on_delete_record_clicked(self) -> None:
    #     active_view = self.__get_active_view()
    #     if not self.__toolbar or not active_view or active_view.mode != ViewMode.READ:
    #         return
    #     self._context.controllers.get_view_controller(active_view.controller_key).on_record_delete()

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
