from typing import Callable
from datetime import datetime

import flet as ft

from utils.translation import Translation
from views.base.base_view import BaseView


class AppView:
    def __init__(self, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__on_create_order: Callable[[], None] | None = None
        self.__on_browse_orders: Callable[[], None] | None = None
        self.__on_cart: Callable[[], None] | None = None
        self.__on_user_settings: Callable[[], None] | None = None
        self.__on_logout: Callable[[], None] | None = None
        self.__auth_container = ft.Container(visible=False, alignment=ft.Alignment.CENTER)
        self.__content_container = ft.Container(expand=True)
        self.__app_name = ft.Text(self.__translation.get("my_erp_companion"), weight=ft.FontWeight.BOLD, size=20)
        self.__app_name_container = ft.Container(
            content=self.__app_name,
            on_click=lambda _: self.__handle_browse_orders(),
            padding=ft.Padding.symmetric(horizontal=4),
        )
        self.__username_text = ft.Text(self.__translation.get("username"))
        self.__username_clickable = ft.Container(
            content=self.__username_text,
            on_click=lambda _: self.__handle_user_settings(),
            padding=ft.Padding.symmetric(horizontal=4),
        )
        self.__cart_count_text = ft.Text("0")
        self.__cart_button = ft.IconButton(
            icon=ft.Icons.SHOPPING_CART_OUTLINED,
            tooltip=self.__translation.get("cart"),
            on_click=lambda _: self.__handle_cart(),
        )
        self.__logout_button = ft.IconButton(
            icon=ft.Icons.LOGOUT,
            tooltip=self.__translation.get("log_out"),
            on_click=lambda _: self.__handle_logout(),
        )
        self.__top_bar = ft.Container(
            visible=False,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.__app_name_container,
                    ft.Row(
                        spacing=8,
                        controls=[
                            self.__cart_button,
                            self.__cart_count_text,
                            self.__username_clickable,
                            self.__logout_button,
                        ],
                    ),
                ],
            ),
        )
        self.__footer_app_name = ft.Text(self.__translation.get("my_erp_companion"), weight=ft.FontWeight.W_600, size=12)
        self.__footer_portal = ft.Text(
            self.__translation.get("footer_web_portal"),
            size=11,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        self.__footer_copy = ft.Text(self.__build_footer_copy(), size=11, color=ft.Colors.ON_SURFACE_VARIANT)
        self.__footer = ft.Container(
            padding=ft.Padding.symmetric(horizontal=24, vertical=10),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
            content=ft.ResponsiveRow(
                columns=12,
                controls=[
                    ft.Container(
                        col={"sm": 12, "md": 7},
                        content=ft.Column(
                            spacing=0,
                            tight=True,
                            controls=[self.__footer_app_name, self.__footer_portal],
                        ),
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        alignment=ft.Alignment.CENTER_RIGHT,
                        content=self.__footer_copy,
                    ),
                ],
            ),
        )
        self.__root = ft.Stack(
            controls=[
                ft.Column(controls=[self.__top_bar, self.__content_container, self.__footer], expand=True),
                self.__auth_container,
            ],
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self._apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__app_name.value = self.__translation.get("my_erp_companion")
        self.__cart_button.tooltip = self.__translation.get("cart")
        self.__logout_button.tooltip = self.__translation.get("log_out")
        self.__footer_app_name.value = self.__translation.get("my_erp_companion")
        self.__footer_portal.value = self.__translation.get("footer_web_portal")
        self.__footer_copy.value = self.__build_footer_copy()
        if not self.__username_text.value:
            self.__username_text.value = self.__translation.get("username")

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

    def set_stack_item(self, view: BaseView | None) -> None:
        self.__content_container.content = view

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self._resolve_theme_mode(theme)
        page.update()

    def set_username(self, username: str | None) -> None:
        if username:
            self.__username_text.value = username
            self.__top_bar.visible = True
        else:
            self.__username_text.value = self.__translation.get("username")
            self.__top_bar.visible = False
        if self.__top_bar.page:
            self.__top_bar.update()

    def set_cart_count(self, count: int) -> None:
        self.__cart_count_text.value = str(max(count, 0))
        if self.__cart_count_text.page:
            self.__cart_count_text.update()

    def set_nav_handlers(self, on_create_order: Callable[[], None], on_browse_orders: Callable[[], None]) -> None:
        self.__on_create_order = on_create_order
        self.__on_browse_orders = on_browse_orders

    def set_cart_handler(self, on_cart: Callable[[], None]) -> None:
        self.__on_cart = on_cart

    def set_user_settings_handler(self, on_user_settings: Callable[[], None]) -> None:
        self.__on_user_settings = on_user_settings

    def set_logout_handler(self, on_logout: Callable[[], None]) -> None:
        self.__on_logout = on_logout

    def __handle_browse_orders(self) -> None:
        if self.__on_browse_orders:
            self.__on_browse_orders()

    def __handle_cart(self) -> None:
        if self.__on_cart:
            self.__on_cart()

    def __handle_user_settings(self) -> None:
        if self.__on_user_settings:
            self.__on_user_settings()

    def __handle_logout(self) -> None:
        if self.__on_logout:
            self.__on_logout()

    def _apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self._resolve_theme_mode(self.__theme)
        if not page.web:
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

    def __build_footer_copy(self) -> str:
        year = datetime.now().year
        app_name = self.__translation.get("my_erp_companion")
        rights = self.__translation.get("all_rights_reserved")
        return f"(c) {year} {app_name}. {rights}"
