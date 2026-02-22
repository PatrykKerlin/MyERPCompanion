from typing import Callable

import flet as ft
from controllers.base.base_controller import BaseController
from styles.styles import AlignmentStyles, AppViewStyles
from utils.translation import Translation
from views.base.base_view import BaseView
from views.components.web_footer_component import WebFooterComponent
from views.components.web_header_component import WebHeaderComponent


class AppView:
    def __init__(self, controller: BaseController, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__header = WebHeaderComponent(controller, self.__translation)
        self.__footer = WebFooterComponent(controller, self.__translation)
        self.__auth_container = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            padding=AppViewStyles.AUTH_OVERLAY_PADDING,
            expand=True,
        )
        self.__content_container = ft.Container(expand=True)
        self.__root = ft.Stack(
            controls=[
                ft.Column(controls=[self.__header, self.__content_container, self.__footer], expand=True),
                self.__auth_container,
            ],
            expand=True,
            alignment=AlignmentStyles.CENTER,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self.__apply_page_settings(page)
        return self.__root

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

    def set_cart_count(self, count: int) -> None:
        self.__header.set_cart_count(count)

    def set_cart_handler(self, on_cart: Callable[[], None]) -> None:
        self.__header.set_cart_handler(on_cart)

    def set_logout_handler(self, on_logout: Callable[[], None]) -> None:
        self.__header.set_logout_handler(on_logout)

    def set_nav_handlers(self, on_browse_orders: Callable[[], None]) -> None:
        self.__header.set_nav_handler(on_browse_orders)

    def set_stack_item(self, view: BaseView | None) -> None:
        self.__content_container.content = view

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self.__resolve_theme_mode(theme)
        page.update()

    def set_user_settings_handler(self, on_user_settings: Callable[[], None]) -> None:
        self.__header.set_user_settings_handler(on_user_settings)

    def set_username(self, username: str | None) -> None:
        self.__header.set_username(username)

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__header.update_translation(self.__translation)
        self.__footer.update_translation(self.__translation)

    def __apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self.__resolve_theme_mode(self.__theme)

    def __resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM
