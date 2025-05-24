from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
import flet.canvas as cv
from views.components import MenuBar, IconsBar, SideMenu

if TYPE_CHECKING:
    from ...controllers.core import AppController


class AppView:
    def __init__(self, page: ft.Page, texts: dict[str, str], theme: str) -> None:
        self._controller: AppController | None = None
        self._page = page
        self._texts = texts
        self.__theme = theme
        self._page.window.width = 1024
        self._page.window.height = 768
        self._page.window.min_width = 800
        self._page.window.min_height = 600
        self._build()

        self.__side_menu_width: float | None = None
        self.__side_menu_shown: bool = True
        self.__side_menu_initialized: bool = False
        self.__side_menu_container: ft.Container | None = None

    def set_controller(self, controller: AppController) -> None:
        self._controller = controller

    def toggle_side_menu(self) -> None:
        if self.__side_menu_container and self.__side_menu_width is not None:
            self.__side_menu_shown = not self.__side_menu_shown
            self.__side_menu_container.width = self.__side_menu_width if self.__side_menu_shown else 0
            self.__side_menu_container.opacity = 1.0 if self.__side_menu_shown else 0.0
            self._page.update()

    def rebuild(self, texts: dict[str, str]) -> None:
        self._texts = texts
        menu_bar = MenuBar(self._texts)
        icons_bar = (
            IconsBar(self._texts, self._controller.toggle_side_menu) if self._controller else ft.MenuBar(controls=[])
        )
        horizontal_divider = ft.Divider(height=1, thickness=1, color=ft.Colors.OUTLINE)
        self.__side_menu_container = ft.Container(
            content=ft.Row(
                controls=[
                    cv.Canvas(
                        content=SideMenu(self._texts),
                        on_resize=self.__on_side_menu_resize,
                        expand=True,
                    ),
                    ft.VerticalDivider(width=1, thickness=1, color=ft.Colors.OUTLINE),
                ],
                expand=True,
            ),
            opacity=1.0,
            animate_opacity=300,
            animate_size=300,
        )
        self._page.clean()
        self._page.overlay.clear()
        self._page.add(
            ft.Column(
                controls=[
                    menu_bar,
                    horizontal_divider,
                    icons_bar,
                    horizontal_divider,
                    ft.Row(
                        controls=[
                            self.__side_menu_container,
                            ft.Container(content=ft.Text("Main content here"), expand=True),
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

    def __on_side_menu_resize(self, e: cv.CanvasResizeEvent) -> None:
        if not self.__side_menu_initialized:
            self.__side_menu_width = int(e.width)
            if self.__side_menu_container:
                self.__side_menu_container.width = self.__side_menu_width
                self.__side_menu_initialized = True
                self._page.update()

    def __resolve_theme(self) -> ft.ThemeMode:
        if self.__theme == "dark":
            return ft.ThemeMode.DARK
        if self.__theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
