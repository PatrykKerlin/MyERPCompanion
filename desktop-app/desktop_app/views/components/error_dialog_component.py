from collections.abc import Callable

import flet as ft

from views.base import BaseDialog


class ErrorDialogComponent(BaseDialog):
    def __init__(
        self,
        texts: dict[str, str],
        message_key: str | None,
        message: str | None,
        on_click: Callable[[ft.ControlEvent], None],
    ) -> None:
        final_message = ""
        if message_key:
            final_message += texts.get(message_key, "")
        if message:
            if final_message:
                final_message += "\n"
            final_message += message
        super().__init__(
            controls=[ft.Text(final_message)],
            actions=[ft.TextButton(texts["ok"], on_click=on_click)],
            title=ft.Row(
                controls=[
                    ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
                    ft.Text(value=texts["error"]),
                ]
            ),
        )
