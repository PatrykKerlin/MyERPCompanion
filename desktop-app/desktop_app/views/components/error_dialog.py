import flet as ft
from views.base import BaseDialog
from collections.abc import Callable


class ErrorDialog(BaseDialog):
    def __init__(self, texts: dict[str, str], message_key: str, on_click: Callable[[ft.ControlEvent], None]) -> None:
        super().__init__(
            texts=texts,
            controls=[ft.Text(texts[message_key])],
            actions=[ft.TextButton(texts["ok"], on_click=on_click)],
            title=ft.Row(
                controls=[
                    ft.Icon(name=ft.Icons.WARNING, color=ft.Colors.RED),
                    ft.Text("Error"),
                ]
            ),
        )
