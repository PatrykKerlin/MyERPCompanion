from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.footer_bar_controller import FooterBarController


class FooterBarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: FooterBarController, texts: dict[str, str]) -> None:
        BaseComponent.__init__(self, controller, texts)
        self.timestamp = ft.Text()
        self.status_message = ft.Text()
        self.status_icon = ft.Icon()
        self.__status_row = ft.Row(
            controls=[
                ft.Text(value=f"{texts["connection_status"]}:"),
                self.status_message,
                self.status_icon,
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

    def set_time(self, value: str) -> None:
        self.timestamp.value = value
        self.timestamp.update()

    def set_status(self, success: bool) -> None:
        if success:
            self.status_message.value = self._texts["connected"]
            self.status_icon.name = ft.Icons.CHECK_OUTLINED
        else:
            self.status_message.value = self._texts["not_connected"]
            self.status_icon.name = ft.Icons.ERROR_OUTLINE
        self.status_message.update()
        self.status_icon.update()
