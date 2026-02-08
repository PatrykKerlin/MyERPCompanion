from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from utils.translation import Translation
    from controllers.components.footer_controller import FooterController


class FooterComponent(BaseComponent, ft.Container):
    def __init__(self, controller: FooterController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__success_message = self._translation.get("connected")
        self.__success_icon = ft.Icons.CHECK_OUTLINED
        self.__error_message = self._translation.get("not_connected")
        self.__error_icon = ft.Icons.ERROR_OUTLINE
        self.__timestamp = ft.Text()
        self.__status_message = ft.Text(self.__success_message)
        self.__status_icon = ft.Icon(self.__success_icon)
        self.__status_row = ft.Row(
            controls=[
                ft.Text(value=f"{self._translation.get('connection_status')}:"),
                self.__status_message,
                self.__status_icon,
            ]
        )
        ft.Container.__init__(
            self,
            content=ft.Row(
                controls=[self.__status_row, ft.Container(expand=True), self.timestamp],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            expand=False,
        )

    @property
    def timestamp(self) -> ft.Text:
        return self.__timestamp

    @property
    def status_message(self) -> ft.Text:
        return self.__status_message

    @property
    def status_icon(self) -> ft.Icon:
        return self.__status_icon

    def set_time(self, value: str) -> None:
        self.__timestamp.value = value
        self.__safe_update(self.__timestamp)

    def set_status(self, success: bool) -> None:
        if success:
            self.__status_message.value = self.__success_message
            self.__status_icon.icon = self.__success_icon
        else:
            self.__status_message.value = self.__error_message
            self.__status_icon.icon = self.__error_icon
        self.__safe_update(self.__status_message)
        self.__safe_update(self.__status_icon)

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
