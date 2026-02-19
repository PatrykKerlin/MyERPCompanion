from __future__ import annotations

from collections.abc import Callable

import flet as ft
from styles.styles import AlignmentStyles, AppViewStyles
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.mixins.input_controls_mixin import InputControlsMixin


class TopBarComponent(InputControlsMixin, ft.Container):
    def __init__(
        self,
        translation: Translation,
        on_menu_click: Callable[[ft.Event[ft.IconButton]], None],
        on_refresh_click: Callable[[ft.Event[ft.IconButton]], None],
        on_user_settings_click: Callable[[], None],
        on_logout_click: Callable[[], None],
    ) -> None:
        self.__translation = translation
        self.__current_username: str | None = None
        self.__on_user_settings_click = on_user_settings_click
        self.__on_logout_click = on_logout_click
        self.__title_text = self._get_label(
            self.__translation.get("my_erp_companion"),
            style=AppViewStyles.MENU_TITLE_STYLE,
        )
        self.__menu_button = self._get_icon_button(
            icon=ft.Icons.MENU,
            on_click=on_menu_click,
        )
        self.__refresh_button = self._get_icon_button(
            icon=ft.Icons.REFRESH,
            on_click=on_refresh_click,
            tooltip=self.__translation.get("refresh"),
        )
        self.__user_menu_button = ft.PopupMenuButton(
            icon=ft.Icons.ACCOUNT_CIRCLE,
            tooltip=self.__translation.get("current_user"),
            items=[],
        )
        self.__refresh_user_menu_items()

        super().__init__(
            visible=False,
            padding=AppViewStyles.TOP_BAR_PADDING,
            border=AppViewStyles.TOP_BAR_BORDER,
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[self.__menu_button, self.__title_text],
                        alignment=AlignmentStyles.AXIS_START,
                        vertical_alignment=AlignmentStyles.CROSS_CENTER,
                        spacing=AppViewStyles.TOP_BAR_LEFT_SPACING,
                    ),
                    ft.Row(
                        controls=[self.__refresh_button, self.__user_menu_button],
                        alignment=AlignmentStyles.AXIS_END,
                        vertical_alignment=AlignmentStyles.CROSS_CENTER,
                        spacing=AppViewStyles.TOP_BAR_RIGHT_SPACING,
                    ),
                ],
                alignment=AppViewStyles.TOP_BAR_ROW_ALIGNMENT,
                vertical_alignment=AppViewStyles.TOP_BAR_ROW_VERTICAL_ALIGNMENT,
            ),
        )

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title_text.value = self.__translation.get("my_erp_companion")
        self.__refresh_button.tooltip = self.__translation.get("refresh")
        self.__user_menu_button.tooltip = self.__translation.get("current_user")
        self.__refresh_user_menu_items()
        BaseComponent.safe_update(self)

    def set_navigation_visible(self, visible: bool) -> None:
        self.visible = visible
        BaseComponent.safe_update(self)

    def set_username(self, username: str | None) -> None:
        self.__current_username = username
        self.__refresh_user_menu_items()
        BaseComponent.safe_update(self)

    def __refresh_user_menu_items(self) -> None:
        username = self.__current_username or self.__translation.get("username")
        self.__user_menu_button.items = [
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            AppViewStyles.USER_MENU_USERNAME_ICON,
                            color=(
                                AppViewStyles.USER_MENU_USERNAME_STYLE.color
                                if AppViewStyles.USER_MENU_USERNAME_STYLE.color is not None
                                else AppViewStyles.USER_MENU_USERNAME_ICON_COLOR
                            ),
                        ),
                        self._get_label(
                            username,
                            style=AppViewStyles.USER_MENU_USERNAME_STYLE,
                        ),
                    ],
                    spacing=AppViewStyles.TOP_BAR_RIGHT_SPACING,
                    vertical_alignment=AlignmentStyles.CROSS_CENTER,
                ),
                mouse_cursor=ft.MouseCursor.BASIC,
                opacity=1.0,
                disabled=True,
            ),
            ft.PopupMenuItem(
                content=ft.Container(
                    content=ft.Divider(
                        height=AppViewStyles.USER_MENU_DIVIDER_HEIGHT,
                        color=AppViewStyles.USER_MENU_DIVIDER_COLOR,
                    ),
                    padding=AppViewStyles.USER_MENU_DIVIDER_PADDING,
                ),
                height=AppViewStyles.USER_MENU_DIVIDER_ITEM_HEIGHT,
                disabled=True,
            ),
            ft.PopupMenuItem(
                icon=ft.Icons.SETTINGS,
                content=self.__translation.get("settings"),
                on_click=self.__on_user_settings_item_click,
            ),
            ft.PopupMenuItem(
                icon=ft.Icons.LOGOUT,
                content=self.__translation.get("log_out"),
                on_click=self.__on_logout_item_click,
            ),
        ]
        BaseComponent.safe_update(self.__user_menu_button)

    def __on_user_settings_item_click(self, _: ft.Event[ft.PopupMenuItem]) -> None:
        self.__on_user_settings_click()

    def __on_logout_item_click(self, _: ft.Event[ft.PopupMenuItem]) -> None:
        self.__on_logout_click()
