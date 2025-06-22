from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base import BaseComponentController
from services.base import BaseService
from utils.view_modes import ViewMode
from views.base import BaseView
from views.components import ToolbarComponent

if TYPE_CHECKING:
    from config.context import Context
    from views.base.base_view import BaseView


class ToolbarController(BaseComponentController[BaseService, ToolbarComponent]):
    def __init__(self, context: Context):
        super().__init__(context)
        self.__side_menu_visible = True
        self.__toolbar: ToolbarComponent | None = None
        self.__side_menu_width: float | None = None

    def get_new_component(self) -> ToolbarComponent:
        self.__toolbar = ToolbarComponent(self, texts=self._context.texts)
        return self.__toolbar

    def on_toggle_menu_clicked(self) -> None:
        side_menu = self._context.controllers.get("side_menu").side_menu
        if not side_menu:
            return
        if not self.__side_menu_width:
            self.__side_menu_width = side_menu.width
        self.__side_menu_visible = not self.__side_menu_visible
        side_menu.width = self.__side_menu_width if self.__side_menu_visible else 0
        side_menu.opacity = 1.0 if self.__side_menu_visible else 0.0
        self._context.page.update()

    def on_lock_view_clicked(self) -> None:
        active_view = self.__get_active_view()
        if not self.__toolbar or not active_view:
            return
        self.__toolbar.set_lock_view_button_icon(unlocked=True)
        self.__toolbar.set_lock_view_button_disabled(disabled=True)
        if active_view.mode == ViewMode.SEARCH:
            active_view.set_create_mode()
        elif active_view.mode == ViewMode.READ:
            active_view.set_edit_mode()

    def on_delete_record_clicked(self) -> None:
        active_view = self.__get_active_view()
        if not self.__toolbar or not active_view or active_view.mode != ViewMode.READ:
            return
        self._context.controllers.get_view_controller(active_view.controller_key).on_record_delete()

    def refresh(self) -> None:
        self.__set_lock_view_button()
        self.__set_delete_record_button()

    def __set_lock_view_button(self) -> None:
        active_view = self.__get_active_view()
        if not self.__toolbar or not active_view:
            return
        self.__toolbar.set_lock_view_button_icon(unlocked=False)
        if active_view.mode in (ViewMode.SEARCH, ViewMode.READ):
            self.__toolbar.set_lock_view_button_disabled(disabled=False)
        else:
            self.__toolbar.set_lock_view_button_disabled(disabled=True)

    def __set_delete_record_button(self) -> None:
        active_view = self.__get_active_view()
        if not self.__toolbar or not active_view:
            return
        if active_view.mode == ViewMode.READ:
            self.__toolbar.set_delete_record_button_disabled(disabled=False)
        else:
            self.__toolbar.set_delete_record_button_disabled(disabled=True)

    def __get_active_view(self) -> BaseView | None:
        active_view_key = self._context.controllers.get("tabs_bar").active_view_key
        return self._context.active_views.get(active_view_key, None)
