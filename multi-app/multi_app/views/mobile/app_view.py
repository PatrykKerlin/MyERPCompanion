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
        content = self.__content_container.content
        if content is not None and hasattr(content, "update_translation"):
            update_translation = getattr(content, "update_translation")
            if callable(update_translation):
                update_translation(translation)

    def set_auth_view(self, component: ft.Control | None) -> None:
        if component is None:
            self.__auth_container.content = None
        else:
            self.__auth_container.content = ft.Column(
                controls=[component],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        self.__auth_container.visible = component is not None

    def set_content(self, component: ft.Control | None) -> None:
        self.__content_container.content = component
        if self.__content_container.page:
            self.__content_container.update()

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
        platform = getattr(page, "platform", None)
        platform_value = getattr(platform, "value", str(platform)).lower()
        if platform_value in {"linux", "windows", "macos"}:
            target_width = 393
            target_height = 852
            if hasattr(page.window, "width"):
                page.window.width = target_width
            if hasattr(page.window, "height"):
                page.window.height = target_height
            if hasattr(page.window, "min_width"):
                page.window.min_width = target_width
            if hasattr(page.window, "min_height"):
                page.window.min_height = target_height
            if hasattr(page.window, "max_width"):
                page.window.max_width = target_width
            if hasattr(page.window, "max_height"):
                page.window.max_height = target_height
            if hasattr(page.window, "resizable"):
                page.window.resizable = False
            if hasattr(page.window, "maximizable"):
                page.window.maximizable = False

    def _resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
