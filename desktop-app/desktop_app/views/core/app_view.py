from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.base.base_view import BaseView
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
        self.__page.window.width = 1600
        self.__page.window.height = 900
        self.__page.window.min_width = 1024
        self.__page.window.min_height = 768
        self.__view_stack = ft.Stack(expand=True)
        self.__build()

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

    def set_view_content(self, current: str, views: dict[str, BaseView]) -> None:
        desired_views: list[BaseView] = list(views.values())
        if not desired_views:
            self.__view_stack.controls.clear()
            self.__page.update()
            return

        desired_ids: set[int] = {id(view) for view in desired_views}
        for existing_view in list(self.__view_stack.controls)[::-1]:
            if id(existing_view) not in desired_ids:
                self.__view_stack.controls.remove(existing_view)

        existing_ids: set[int] = {id(view) for view in self.__view_stack.controls}
        for view in desired_views:
            if id(view) not in existing_ids:
                self.__view_stack.controls.append(view)

        self.__view_stack.controls[:] = desired_views

        current_view: BaseView | None = views.get(current) if current else None
        for view in self.__view_stack.controls:
            view.visible = (view is current_view) if current_view else False

        self.__page.update()
