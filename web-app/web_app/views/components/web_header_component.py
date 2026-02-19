from collections.abc import Callable

import flet as ft
from controllers.base.base_controller import BaseController
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, AppViewStyles, ButtonStyles, TypographyStyles
from utils.translation import Translation
from views.base.base_component import BaseComponent


class WebHeaderComponent(BaseComponent[BaseController], ft.Container):
    def __init__(self, controller: BaseController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__current_username: str | None = None
        self.__on_browse_orders: Callable[[], None] | None = None
        self.__on_cart: Callable[[], None] | None = None
        self.__on_user_settings: Callable[[], None] | None = None
        self.__on_logout: Callable[[], None] | None = None

        self.__app_name = self._get_label(self._translation.get("my_erp_companion"), style=TypographyStyles.APP_HEADER)
        self.__app_name_container = ft.Container(
            content=self.__app_name,
            on_click=lambda _: self.__handle_browse_orders(),
            padding=AppViewStyles.CLICKABLE_TEXT_PADDING,
        )
        self.__cart_button = ft.TextButton(
            content="0",
            icon=ft.Icon(
                ft.Icons.SHOPPING_CART_OUTLINED,
                size=AppViewStyles.TOP_BAR_ICON_SIZE,
            ),
            tooltip=self._translation.get("cart"),
            on_click=lambda _: self.__handle_cart(),
            style=ButtonStyles.top_bar_info,
        )
        self.__username_button = ft.TextButton(
            content=self._translation.get("username"),
            icon=ft.Icon(
                ft.Icons.PERSON_OUTLINE,
                size=AppViewStyles.TOP_BAR_ICON_SIZE,
            ),
            tooltip=self._translation.get("current_user"),
            on_click=lambda _: self.__handle_user_settings(),
            style=ButtonStyles.top_bar_info,
        )
        self.__logout_button = ft.IconButton(
            icon=ft.Icons.LOGOUT,
            tooltip=self._translation.get("log_out"),
            on_click=lambda _: self.__handle_logout(),
            style=ButtonStyles.icon,
        )

        ft.Container.__init__(
            self,
            visible=False,
            padding=AppViewStyles.TOP_BAR_PADDING,
            border=AppViewStyles.TOP_BAR_BORDER,
            content=ft.Row(
                alignment=AlignmentStyles.AXIS_SPACE_BETWEEN,
                vertical_alignment=AlignmentStyles.CROSS_CENTER,
                controls=[
                    self.__app_name_container,
                    ft.Row(
                        spacing=AppDimensions.SPACE_SM,
                        controls=[
                            self.__cart_button,
                            self.__username_button,
                            self.__logout_button,
                        ],
                    ),
                ],
            ),
        )

    def set_cart_count(self, count: int) -> None:
        safe_count = max(count, 0)
        self.__cart_button.content = "99+" if safe_count > 99 else str(safe_count)
        self._safe_update(self.__cart_button)

    def set_cart_handler(self, on_cart: Callable[[], None]) -> None:
        self.__on_cart = on_cart

    def set_logout_handler(self, on_logout: Callable[[], None]) -> None:
        self.__on_logout = on_logout

    def set_nav_handler(self, on_browse_orders: Callable[[], None]) -> None:
        self.__on_browse_orders = on_browse_orders

    def set_user_settings_handler(self, on_user_settings: Callable[[], None]) -> None:
        self.__on_user_settings = on_user_settings

    def set_username(self, username: str | None) -> None:
        self.__current_username = username
        if username:
            self.__username_button.content = username
            self.visible = True
        else:
            self.__username_button.content = self._translation.get("username")
            self.visible = False
        self._safe_update(self)

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__app_name.value = self._translation.get("my_erp_companion")
        self.__cart_button.tooltip = self._translation.get("cart")
        self.__username_button.tooltip = self._translation.get("current_user")
        self.__logout_button.tooltip = self._translation.get("log_out")
        if self.__current_username:
            self.__username_button.content = self.__current_username
        else:
            self.__username_button.content = self._translation.get("username")
        self._safe_update(self)

    def __handle_browse_orders(self) -> None:
        if self.__on_browse_orders:
            self.__on_browse_orders()

    def __handle_cart(self) -> None:
        if self.__on_cart:
            self.__on_cart()

    def __handle_logout(self) -> None:
        if self.__on_logout:
            self.__on_logout()

    def __handle_user_settings(self) -> None:
        if self.__on_user_settings:
            self.__on_user_settings()
