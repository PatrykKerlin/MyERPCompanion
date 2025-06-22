from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from styles import MenuStyles

from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.toolbar_controller import ToolbarController


class ToolbarComponent(BaseComponent, ft.MenuBar):
    def __init__(self, controller: ToolbarController, texts: dict[str, str]) -> None:
        BaseComponent.__init__(self, controller, texts)
        self.__toggle_menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip=texts["hide_menu"],
            on_click=lambda _: controller.on_toggle_menu_clicked(),
        )
        self.__lock_view_button = ft.IconButton(
            icon=ft.Icons.LOCK,
            tooltip=texts["unlock_form"],
            disabled=True,
            on_click=lambda _: controller.on_lock_view_clicked(),
        )
        self.__delete_record_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip=texts["delete_record"],
            disabled=True,
            on_click=lambda _: controller.on_delete_record_clicked(),
        )
        ft.MenuBar.__init__(
            self,
            style=MenuStyles.flat,
            controls=[self.__toggle_menu_button, self.__lock_view_button, self.__delete_record_button],
        )

    def set_lock_view_button_icon(self, unlocked: bool) -> None:
        locked_icon = ft.Icons.LOCK
        unlocked_icon = ft.Icons.LOCK_OPEN
        if unlocked and self.__lock_view_button.icon == locked_icon:
            self.__lock_view_button.icon = unlocked_icon
        elif not unlocked and self.__lock_view_button.icon == unlocked_icon:
            self.__lock_view_button.icon = locked_icon
        self.__lock_view_button.update()

    def set_lock_view_button_disabled(self, disabled: bool) -> None:
        if disabled and not self.__lock_view_button.disabled:
            self.__lock_view_button.disabled = True
        elif not disabled and self.__lock_view_button.disabled:
            self.__lock_view_button.disabled = False
        self.__lock_view_button.update()

    def set_delete_record_button_disabled(self, disabled: bool) -> None:
        if disabled and not self.__delete_record_button.disabled:
            self.__delete_record_button.disabled = True
        elif not disabled and self.__delete_record_button.disabled:
            self.__delete_record_button.disabled = False
        self.__delete_record_button.update()
