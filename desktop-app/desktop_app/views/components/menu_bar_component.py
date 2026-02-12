from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.components.menu_bar_controller import MenuBarController
    from utils.translation import Translation


class MenuBarComponent(BaseComponent, ft.MenuBar):
    def __init__(self, controller: MenuBarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)

        def label_with_shortcut(key: str, shortcut: str | None = None) -> ft.Text:
            label = self._translation.get(key)
            if shortcut:
                return ft.Text(
                    spans=[
                        ft.TextSpan(label),
                        ft.TextSpan(
                            f"  {shortcut}",
                            style=ft.TextStyle(
                                size=10,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ),
                    ]
                )
            return ft.Text(label)

        ft.MenuBar.__init__(
            self,
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("file")),
                    controls=[
                        ft.MenuItemButton(
                            content=label_with_shortcut("new", "Ctrl+N"),
                            on_click=lambda _: self._controller.on_new_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("search", "Ctrl+O"),
                            on_click=lambda _: self._controller.on_search_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("save", "Ctrl+S"),
                            on_click=lambda _: self._controller.on_save_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("close_tab", "Ctrl+W"),
                            on_click=lambda _: self._controller.on_close_tab_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("close_other_tabs", "Ctrl+Shift+O"),
                            on_click=lambda _: self._controller.on_close_other_tabs_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("close_all_tabs", "Ctrl+Shift+W"),
                            on_click=lambda _: self._controller.on_close_all_tabs_clicked(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("edit")),
                    controls=[
                        ft.MenuItemButton(
                            content=label_with_shortcut("undo", "Ctrl+Z"),
                            on_click=lambda _: self._controller.on_undo_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("redo", "Ctrl+Y"),
                            on_click=lambda _: self._controller.on_redo_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("copy_form_data", "Ctrl+Shift+C"),
                            on_click=lambda _: self._controller.on_copy_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("paste_form_data", "Ctrl+Shift+V"),
                            on_click=lambda _: self._controller.on_paste_clicked(),
                        ),
                        ft.MenuItemButton(
                            content=label_with_shortcut("find_tab", "Ctrl+F"),
                            on_click=lambda _: self._controller.on_find_tab_clicked(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(self._translation.get("view")),
                    controls=[
                        ft.MenuItemButton(
                            content=label_with_shortcut("refresh", "Ctrl+R"),
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
