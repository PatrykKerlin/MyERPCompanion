from __future__ import annotations

from typing import TYPE_CHECKING
import flet as ft


from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from utils.translation import Translation
    from controllers.components.menu_bar_controller import MenuBarController


class MenuBarComponent(BaseComponent, ft.MenuBar):
    def __init__(self, controller: MenuBarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        ft.MenuBar.__init__(
            self,
            
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("file")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("new")),
                            trailing=ft.Text("Ctrl+N"),
                            on_click=lambda _: self._controller.on_new_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("open")),
                            trailing=ft.Text("Ctrl+O"),
                            on_click=lambda _: self._controller.on_open_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("save")),
                            trailing=ft.Text("Ctrl+S"),
                            on_click=lambda _: self._controller.on_save_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("close_tab")),
                            trailing=ft.Text("Ctrl+W"),
                            on_click=lambda _: self._controller.on_close_tab_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("close_other_tabs")),
                            trailing=ft.Text("Ctrl+Shift+O"),
                            on_click=lambda _: self._controller.on_close_other_tabs_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("close_all_tabs")),
                            trailing=ft.Text("Ctrl+Shift+W"),
                            on_click=lambda _: self._controller.on_close_all_tabs_clicked(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("edit")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("undo")),
                            trailing=ft.Text("Ctrl+Z"),
                            on_click=lambda _: self._controller.on_undo_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("redo")),
                            trailing=ft.Text("Ctrl+Y"),
                            on_click=lambda _: self._controller.on_redo_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("copy")),
                            trailing=ft.Text("Ctrl+C"),
                            on_click=lambda _: self._controller.on_copy_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("paste")),
                            trailing=ft.Text("Ctrl+V"),
                            on_click=lambda _: self._controller.on_paste_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("find_tab")),
                            trailing=ft.Text("Ctrl+F"),
                            on_click=lambda _: self._controller.on_find_tab_clicked(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("view")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("refresh")),
                            trailing=ft.Text("Ctrl+R"),
                            on_click=lambda _: self._controller.on_refresh_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("toggle_side_menu")),
                            on_click=lambda _: self._controller.on_toggle_side_menu_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("toggle_toolbar")),
                            on_click=lambda _: self._controller.on_toggle_toolbar_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("toggle_tabs_bar")),
                            on_click=lambda _: self._controller.on_toggle_tabs_bar_clicked(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("help")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("about")),
                            on_click=lambda _: self._controller.on_about_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(self._translation.get("check_api_status")),
                            on_click=lambda _: self._controller.on_check_api_status_clicked(),
                        ),
                    ],
                ),
            ],
        )
