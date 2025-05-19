import flet as ft
from views.components import MenuBar
import threading


class AppView:
    def __init__(self, page: ft.Page, texts: dict[str, str], theme: str) -> None:
        self._page = page
        self._texts = texts
        self.__theme = theme
        self._page.window.width = 1024
        self._page.window.height = 768
        self._page.window.min_width = 800
        self._page.window.min_height = 600
        self._build()

    def _build(self) -> None:
        self._page.title = self._texts["myerpcompanion"]
        self._page.theme_mode = self.__resolve_theme()
        self._page.update()

    def rebuild(self, texts: dict[str, str]) -> None:
        self._texts = texts
        self._page.clean()
        self._page.overlay.clear()
        self._page.add(ft.Column(controls=[MenuBar(self._texts)]))
        self._build()
        self._page.update()

    def __resolve_theme(self) -> ft.ThemeMode:
        if self.__theme == "dark":
            return ft.ThemeMode.DARK
        elif self.__theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
