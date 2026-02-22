import asyncio

import flet as ft
from styles.colors import AppColors
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ConfirmDialogComponent(BaseDialog):
    def __init__(self, translation: Translation, message_key: str) -> None:
        self.__future = asyncio.get_running_loop().create_future()
        cancel_button = ft.Button(
            content=translation.get("cancel"),
            on_click=lambda _: self.__set_result(False),
            style=ButtonStyles.regular,
        )
        confirm_button = ft.Button(
            content=translation.get("ok"),
            on_click=lambda _: self.__set_result(True),
            style=ButtonStyles.primary_compact,
        )
        super().__init__(
            controls=[ft.Text(translation.get(message_key))],
            actions=[cancel_button, confirm_button],
            title=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.WARNING, color=AppColors.WARNING),
                    ft.Text(value=translation.get("are_you_sure")),
                ]
            ),
        )

    @property
    def future(self) -> asyncio.Future[bool]:
        return self.__future

    def __set_result(self, result: bool) -> None:
        if not self.__future.done():
            self.__future.set_result(result)
