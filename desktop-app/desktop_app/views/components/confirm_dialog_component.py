import asyncio

import flet as ft

from views.base import BaseDialog


class ConfirmDialogComponent(BaseDialog):
    def __init__(
        self,
        texts: dict[str, str],
        message_key: str,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self.__loop = loop
        self.__future = self.__loop.create_future()
        cancel_button = ft.Button(
            text=texts["cancel"],
            on_click=lambda _: self.__set_result(False),
        )
        confirm_button = ft.ElevatedButton(
            text=texts["ok"],
            on_click=lambda _: self.__set_result(True),
        )
        super().__init__(
            controls=[ft.Text(texts[message_key])],
            actions=[cancel_button, confirm_button],
            title=ft.Row(
                controls=[
                    ft.Icon(name=ft.Icons.WARNING, color=ft.Colors.ORANGE),
                    ft.Text(value=texts["are_you_sure"]),
                ]
            ),
        )

    @property
    def future(self) -> asyncio.Future[bool]:
        return self.__future

    def __set_result(self, result: bool) -> None:
        if not self.__future.done():
            self.__future.set_result(result)
