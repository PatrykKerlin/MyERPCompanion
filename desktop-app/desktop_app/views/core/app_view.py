from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from views.components.menu_bar import MenuBar


if TYPE_CHECKING:
    from controllers.core.app_controller import AppController
    from schemas.core.user_schema import UserInputSchema
    from views.components.buttons_bar import ButtonsBar
    from views.components.side_menu import SideMenu
    from views.components.tabs_bar import TabsBar


class AppView:
    def __init__(self, page: ft.Page, texts: dict[str, str], theme: str) -> None:
        self._controller: AppController | None = None
        self._page = page
        self._texts = texts
        self.__theme = theme
        self.__user: UserInputSchema | None = None
        self.__view_container: ft.Container | None = None

        self._page.window.width = 1024
        self._page.window.height = 768
        self._page.window.min_width = 800
        self._page.window.min_height = 600

        self._build()

    def set_controller(self, controller: AppController) -> None:
        self._controller = controller

    def set_user(self, user: UserInputSchema) -> None:
        self.__user = user

    def set_view_content(self, content: ft.Control) -> None:
        if self.__view_container:
            self.__view_container.content = content
            self._page.update()

    def rebuild(self, texts: dict[str, str], side_menu: SideMenu, buttons_bar: ButtonsBar, tabs_bar: TabsBar) -> None:
        if not self.__user:
            return

        self._texts = texts
        menu_bar = MenuBar(self._texts)
        horizontal_divider = ft.Divider(height=1, thickness=1, color=ft.Colors.OUTLINE)

        self.__view_container = ft.Container(expand=True)

        self._page.clean()
        self._page.overlay.clear()
        self._page.add(
            ft.Column(
                controls=[
                    menu_bar,
                    horizontal_divider,
                    buttons_bar,
                    horizontal_divider,
                    ft.Row(
                        controls=[
                            side_menu,
                            ft.Column(
                                controls=[
                                    tabs_bar,
                                    self.__view_container,
                                ],
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
            )
        )
        self._build()
        self._page.update()

    def _build(self) -> None:
        self._page.title = self._texts["myerpcompanion"]
        self._page.theme_mode = self.__resolve_theme()
        self._page.update()

    def __resolve_theme(self) -> ft.ThemeMode:
        if self.__theme == "dark":
            return ft.ThemeMode.DARK
        if self.__theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
