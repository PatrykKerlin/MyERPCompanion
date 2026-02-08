import flet as ft

from utils.translation import Translation


class AppView:
    def __init__(self, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__content_container = ft.Container(expand=True, visible=False)
        self.__auth_container = ft.Container(visible=False, expand=True, alignment=ft.Alignment.CENTER)
        self.__root = ft.Stack(
            controls=[self.__content_container, self.__auth_container],
            expand=True,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self._apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation

    def set_auth_view(self, component: ft.Control | None) -> None:
        self.__auth_container.content = component
        self.__auth_container.visible = component is not None

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self._resolve_theme_mode(theme)
        page.update()

    def set_content_visible(self, visible: bool) -> None:
        self.__content_container.visible = visible
        if self.__content_container.page:
            self.__content_container.update()

    def _apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self._resolve_theme_mode(self.__theme)
        page.padding = 0
        page.adaptive = True
        platform = str(getattr(page, "platform", "")).lower()
        if platform in {"linux", "windows", "macos"}:
            if hasattr(page.window, "width"):
                page.window.width = 430
            if hasattr(page.window, "height"):
                page.window.height = 932
            if hasattr(page.window, "min_width"):
                page.window.min_width = 360
            if hasattr(page.window, "min_height"):
                page.window.min_height = 640

    def _resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
