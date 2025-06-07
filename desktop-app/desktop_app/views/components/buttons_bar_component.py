from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from styles import MenuStyles

from views.base import BaseView

if TYPE_CHECKING:
    from controllers.components.buttons_bar_controller import ButtonsBarController


class ButtonsBarComponent(BaseView, ft.MenuBar):
    def __init__(self, controller: ButtonsBarController, texts: dict[str, str]) -> None:
        BaseView.__init__(self, controller, texts)
        ft.MenuBar.__init__(
            self,
            style=MenuStyles.flat,
            controls=[
                ft.MenuItemButton(
                    leading=ft.Icon(ft.Icons.MENU),
                    tooltip=texts["hide_menu"],
                    on_click=lambda _: controller.toggle_side_menu(),
                ),
            ],
        )
