from __future__ import annotations
from typing import TYPE_CHECKING, cast
import flet as ft

from controllers.base import BaseComponentController
from services.base import BaseService
from views.base import BaseView
from views.components import ButtonsBarComponent, SideMenuComponent
from utils.view_modes import ViewMode

if TYPE_CHECKING:
    from config.context import Context


class ButtonsBarController(BaseComponentController[BaseService, ButtonsBarComponent]):
    def __init__(self, context: Context):
        super().__init__(context)
        self.__side_menu_visible = True
        self.__buttons_bar: ButtonsBarComponent | None = None

    @property
    def component(self) -> ButtonsBarComponent:
        self.__buttons_bar = ButtonsBarComponent(self, texts=self._context.texts)
        return self.__buttons_bar

    def toggle_side_menu_button(self) -> None:
        side_menu = self.__get_side_menu()
        if not side_menu:
            return
        self.__side_menu_visible = not self.__side_menu_visible
        side_menu.width = side_menu.calculated_width if self.__side_menu_visible else 0
        side_menu.opacity = 1.0 if self.__side_menu_visible else 0.0
        self._context.page.update()

    def toggle_lock_view_button(self) -> None:
        if not self.__buttons_bar:
            return
        active_view_key = self._context.controllers.get("tabs_bar").active_view_key
        if not active_view_key:
            return
        active_view = cast(BaseView, self._context.active_views[active_view_key])
        if active_view.mode == ViewMode.SEARCH:
            self.__buttons_bar.set_lock_view_button_icon(unlocked=True)
            self.set_lock_view_button_disabled(disabled=True)
            active_view.set_create_mode()
        elif active_view.mode == ViewMode.READ:
            self.__buttons_bar.set_lock_view_button_icon(unlocked=True)
            self.set_lock_view_button_disabled(disabled=True)
            active_view.set_edit_mode()

    def set_lock_view_button_disabled(self, disabled: bool) -> None:
        if not self.__buttons_bar:
            return
        self.__buttons_bar.set_lock_view_button_disabled(disabled)

    def __get_side_menu(self) -> SideMenuComponent | None:
        column = self._context.page.controls[0] if self._context.page.controls else []
        column = cast(ft.Column, column)
        row = column.controls[4]
        row = cast(ft.Row, row)
        return row.controls[0] if isinstance(row.controls[0], SideMenuComponent) else None
