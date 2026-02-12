from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.components.toolbar_controller import ToolbarController
    from utils.translation import Translation


class ToolbarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: ToolbarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__toggle_menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip=translation.get("hide_menu"),
            on_click=lambda _: self._controller.on_toggle_menu_clicked(),
        )
        self.__lock_view_button = ft.IconButton(
            icon=ft.Icons.LOCK,
            tooltip=translation.get("unlock_form"),
            disabled=True,
            on_click=lambda _: self._controller.on_lock_view_clicked(),
        )
        self.__delete_record_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip=translation.get("delete_record"),
            disabled=True,
            on_click=lambda _: self._controller.on_delete_clicked(),
        )
        self.__nav_spacer = ft.Container(width=12)
        self.__first_tab_button = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            tooltip=translation.get("First tab"),
            disabled=True,
            on_click=lambda _: self._controller.on_first_tab_clicked(),
        )
        self.__previous_tab_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            tooltip=translation.get("Previous tab"),
            disabled=True,
            on_click=lambda _: self._controller.on_previous_tab_clicked(),
        )
        self.__search_tab_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip=translation.get("Find tab"),
            disabled=True,
            on_click=lambda _: self._controller.on_search_tab_clicked(),
        )
        self.__close_other_tabs_button = ft.IconButton(
            icon=ft.Icons.CLOSE_FULLSCREEN,
            tooltip=translation.get("Close other tabs"),
            disabled=True,
            on_click=lambda _: self._controller.on_close_other_tabs_clicked(),
        )
        self.__close_all_tabs_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip=translation.get("Close all tabs"),
            disabled=True,
            on_click=lambda _: self._controller.on_close_all_tabs_clicked(),
        )
        self.__next_tab_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            tooltip=translation.get("Next tab"),
            disabled=True,
            on_click=lambda _: self._controller.on_next_tab_clicked(),
        )
        self.__last_tab_button = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            tooltip=translation.get("Last tab"),
            disabled=True,
            on_click=lambda _: self._controller.on_last_tab_clicked(),
        )
        self.__refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip=translation.get("refresh"),
            disabled=True,
            on_click=lambda _: self._controller.on_refresh_clicked(),
        )
        self.__user_label = ft.Text("")
        self.__pending_username: str | None = None
        self.__user_button = ft.IconButton(
            icon=ft.Icons.PERSON,
            tooltip=translation.get("open_user"),
            disabled=True,
            on_click=lambda _: self._controller.on_current_user_clicked(),
        )
        self.__logout_button = ft.IconButton(
            icon=ft.Icons.LOGOUT,
            tooltip=translation.get("log_out"),
            disabled=True,
            on_click=lambda _: self._controller.on_logout_clicked(),
        )
        self.__user_row = ft.Row(
            controls=[self.__user_label, self.__user_button, self.__logout_button],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.__left_row = ft.Row(
            controls=[
                self.__toggle_menu_button,
                self.__lock_view_button,
                self.__delete_record_button,
                self.__nav_spacer,
                self.__first_tab_button,
                self.__previous_tab_button,
                self.__search_tab_button,
                self.__next_tab_button,
                self.__last_tab_button,
                self.__close_other_tabs_button,
                self.__close_all_tabs_button,
                self.__refresh_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.__main_row = ft.Row(
            controls=[self.__left_row, self.__user_row],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        ft.Container.__init__(
            self,
            content=self.__main_row,
            expand=True,
        )

    def set_lock_view_button_icon(self, unlocked: bool) -> None:
        locked_icon = ft.Icons.LOCK
        unlocked_icon = ft.Icons.LOCK_OPEN
        if unlocked and self.__lock_view_button.icon == locked_icon:
            self.__lock_view_button.icon = unlocked_icon
        elif not unlocked and self.__lock_view_button.icon == unlocked_icon:
            self.__lock_view_button.icon = locked_icon
        self.__lock_view_button.update()

    def set_lock_view_button_state(self, disabled: bool) -> None:
        if disabled and not self.__lock_view_button.disabled:
            self.__lock_view_button.disabled = True
        elif not disabled and self.__lock_view_button.disabled:
            self.__lock_view_button.disabled = False
        self.__lock_view_button.update()

    def set_delete_button_state(self, disabled: bool) -> None:
        if disabled and not self.__delete_record_button.disabled:
            self.__delete_record_button.disabled = True
        elif not disabled and self.__delete_record_button.disabled:
            self.__delete_record_button.disabled = False
        self.__delete_record_button.update()

    def set_navigation_buttons_state(self, disabled: bool) -> None:
        buttons = [
            self.__first_tab_button,
            self.__previous_tab_button,
            self.__search_tab_button,
            self.__close_other_tabs_button,
            self.__close_all_tabs_button,
            self.__next_tab_button,
            self.__last_tab_button,
            self.__refresh_button,
        ]
        for button in buttons:
            if disabled and not button.disabled:
                button.disabled = True
            elif not disabled and button.disabled:
                button.disabled = False
            button.update()

    def did_mount(self):
        if self.__pending_username is not None:
            self.__apply_pending_username()
        return super().did_mount()

    def set_current_user(self, username: str | None) -> None:
        self.__pending_username = username
        try:
            page = self.page
        except RuntimeError:
            return
        if page is not None:
            self.__apply_pending_username()

    def __apply_pending_username(self) -> None:
        username = self.__pending_username
        if username:
            self.__user_label.value = username
            self.__user_button.disabled = False
            self.__logout_button.disabled = False
        else:
            self.__user_label.value = ""
            self.__user_button.disabled = True
            self.__logout_button.disabled = True
        self.__user_label.update()
        self.__user_button.update()
        self.__logout_button.update()
