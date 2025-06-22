from collections.abc import Callable

import flet as ft

from views.base import BaseDialog


class MessageDialogComponent(BaseDialog):
    def __init__(self, texts: dict[str, str], message_key: str, on_click: Callable[[], None]) -> None:
        super().__init__(
            controls=[ft.Text(texts[message_key])],
            actions=[ft.TextButton(texts["ok"], on_click=lambda _: on_click())],
        )
