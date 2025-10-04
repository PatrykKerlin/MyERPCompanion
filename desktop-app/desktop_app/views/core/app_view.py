from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.components.footer_component import FooterComponent
from views.components.menu_bar_component import MenuBarComponent
from views.components.side_menu_component import SideMenuComponent
from views.components.tabs_bar_component import TabsBarComponent
from views.components.toolbar_component import ToolbarComponent

if TYPE_CHECKING:
    from utils.translation import Translation


class AppView:
    def __init__(self, page: ft.Page, translation: Translation, theme: str) -> None:
        self.__page = page
        self.__translation = translation
        self.__theme = theme
        self.__page.window.width = 1024
        self.__page.window.height = 768
        self.__page.window.min_width = 800
        self.__page.window.min_height = 600
        self.__view_stack = ft.Stack(expand=True)
        self.__build()

    @property
    def view_stack(self) -> ft.Stack:
        return self.__view_stack

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__page.update()

    def __build(self) -> None:
        self.__page.title = self.__translation.get("my_erp_companion")
        self.__page.theme_mode = self.__resolve_theme()
        self.__page.update()

    def __resolve_theme(self) -> ft.ThemeMode:
        if self.__theme == "dark":
            return ft.ThemeMode.DARK
        if self.__theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM

    def rebuild(
        self,
        menu_bar: MenuBarComponent,
        side_menu: SideMenuComponent,
        toolbar: ToolbarComponent,
        tabs_bar: TabsBarComponent,
        footer: FooterComponent,
    ) -> None:
        horizontal_divider = ft.Divider(height=1, thickness=1, color=ft.Colors.OUTLINE)
        vertical_divider = ft.VerticalDivider(width=1, thickness=1, color=ft.Colors.OUTLINE)

        self.__page.clean()
        self.__page.overlay.clear()
        self.__page.add(
            ft.Column(
                controls=[
                    menu_bar,
                    horizontal_divider,
                    toolbar,
                    horizontal_divider,
                    ft.Row(
                        controls=[
                            side_menu,
                            vertical_divider,
                            ft.Column(
                                controls=[
                                    tabs_bar,
                                    self.__view_stack,
                                ],
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                    horizontal_divider,
                    footer,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
            )
        )
        self.__build()
        self.__page.update()

    def set_view_content(self, content: ft.Control) -> None:
        if not self.__view_stack:
            return
        if content not in self.__view_stack.controls:
            self.__view_stack.controls.append(content)
        for view in self.__view_stack.controls:
            view.visible = view == content
        self.__page.update()
