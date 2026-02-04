import flet as ft

from utils.translation import Translation
from views.base.base_view import BaseView


class AppView:
    def __init__(self, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__auth_container = ft.Container(visible=False, expand=True)
        self.__content_container = ft.Container(expand=True)
        self.__username_text = ft.Text("")
        self.__top_bar = ft.Container(
            visible=False,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.TextButton(self.__translation.get("create_order"), on_click=lambda _: None),
                            ft.TextButton(self.__translation.get("browse_orders"), on_click=lambda _: None),
                        ],
                    ),
                    self.__username_text,
                ],
            ),
        )
        self.__root = ft.Stack(
            controls=[
                ft.Column(controls=[self.__top_bar, self.__content_container], expand=True),
                self.__auth_container,
            ],
            expand=True,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self._apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        left_controls = self.__top_bar.content.controls[0].controls
        left_controls[0].text = self.__translation.get("create_order")
        left_controls[1].text = self.__translation.get("browse_orders")
        if not self.__username_text.value:
            self.__username_text.value = self.__translation.get("username")

    def set_auth_view(self, component: ft.Control | None) -> None:
        self.__auth_container.content = component
        self.__auth_container.visible = component is not None

    def set_stack_item(self, view: BaseView | None) -> None:
        self.__content_container.content = view

    def set_username(self, username: str | None) -> None:
        if username:
            self.__username_text.value = username
        else:
            self.__username_text.value = self.__translation.get("username")
        self.__top_bar.visible = True
        if self.__top_bar.page:
            self.__top_bar.update()

    def _apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self._resolve_theme_mode(self.__theme)
        page.window.width = 1600
        page.window.height = 900
        page.window.min_width = 1024
        page.window.min_height = 768

    def _resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
