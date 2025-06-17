from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from styles import MenuStyles

from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.buttons_bar_controller import ButtonsBarController


class ButtonsBarComponent(BaseComponent, ft.MenuBar):
    def __init__(self, controller: ButtonsBarController, texts: dict[str, str]) -> None:
        BaseComponent.__init__(self, controller, texts)
        self.toggle_menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip=texts["hide_menu"],
            on_click=lambda _: controller.toggle_side_menu_button(),
        )
        self.lock_view_button = ft.IconButton(
            icon=ft.Icons.LOCK,
            tooltip=texts["hide_menu"],
            disabled=True,
            on_click=lambda _: controller.toggle_lock_view_button(),
        )
        ft.MenuBar.__init__(
            self,
            style=MenuStyles.flat,
            controls=[self.toggle_menu_button, self.lock_view_button],
        )

    def set_lock_view_button_icon(self, unlocked: bool) -> None:
        locked_icon = ft.Icons.LOCK
        unlocked_icon = ft.Icons.LOCK_OPEN
        if unlocked and self.lock_view_button.icon == locked_icon:
            self.lock_view_button.icon = unlocked_icon
        elif not unlocked and self.lock_view_button.icon == unlocked_icon:
            self.lock_view_button.icon = locked_icon
        self.lock_view_button.update()

    def set_lock_view_button_disabled(self, disabled: bool) -> None:
        if disabled and not self.lock_view_button.disabled:
            self.lock_view_button.disabled = True
        elif not disabled and self.lock_view_button.disabled:
            self.lock_view_button.disabled = False
        self.lock_view_button.update()
