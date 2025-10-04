from __future__ import annotations

from typing import TYPE_CHECKING
import flet as ft

# from styles import MenuStyles
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from utils.translation import Translation
    from controllers.components.menu_bar_controller import MenuBarController


class MenuBarComponent(BaseComponent, ft.MenuBar):
    def __init__(self, controller: MenuBarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        ft.MenuBar.__init__(
            self,
            # style=MenuStyles.flat,
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("file")),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(self._translation.get("new"))),
                        ft.MenuItemButton(content=ft.Text(self._translation.get("open"))),
                        ft.MenuItemButton(content=ft.Text(self._translation.get("exit"))),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("edit")),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(self._translation.get("undo"))),
                        ft.MenuItemButton(content=ft.Text(self._translation.get("redo"))),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("help")),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(self._translation.get("about"))),
                    ],
                ),
            ],
        )
