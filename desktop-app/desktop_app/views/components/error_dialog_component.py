from collections.abc import Callable

import flet as ft

from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ErrorDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        message_key: str | None,
        message: str | None,
        on_click: Callable[[ft.ControlEvent], None],
    ) -> None:
        final_message = ""
        if message_key:
            final_message += translation.get(message_key)
        if message:
            if final_message:
                final_message += "\n"
            final_message += message
        super().__init__(
            controls=[ft.Text(final_message)],
            actions=[ft.TextButton(translation.get("ok"), on_click=on_click)],
            title=ft.Row(
                controls=[
                    ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
                    ft.Text(value=translation.get("error")),
                ]
            ),
        )
