from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.footer_controller import FooterController


class FooterComponent(BaseComponent, ft.Container):
    def __init__(self, controller: FooterController, texts: dict[str, str]) -> None:
        BaseComponent.__init__(self, controller, texts)
        self.__timestamp = ft.Text()
        self.__status_message = ft.Text()
        self.__status_icon = ft.Icon()
        self.__status_row = ft.Row(
            controls=[
                ft.Text(value=f"{texts["connection_status"]}:"),
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
        self.__timestamp.update()

    def set_status(self, success: bool) -> None:
        if success:
            self.__status_message.value = self._texts["connected"]
            self.__status_icon.name = ft.Icons.CHECK_OUTLINED
        else:
            self.__status_message.value = self._texts["not_connected"]
            self.__status_icon.name = ft.Icons.ERROR_OUTLINE
        self.__status_message.update()
        self.__status_icon.update()
