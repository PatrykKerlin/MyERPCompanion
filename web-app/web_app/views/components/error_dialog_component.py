from collections.abc import Callable
from typing import cast

import flet as ft
from styles.styles import ButtonStyles, FeedbackStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ErrorDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        message_key: str | None,
        message: str | None,
        on_ok_clicked: Callable[[ft.Event[ft.TextButton]], ft.DialogControl | None],
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
            actions=cast(
                list[ft.Control],
                [ft.TextButton(translation.get("ok"), on_click=on_ok_clicked, style=ButtonStyles.primary_regular)],
            ),
            title=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.ERROR, color=FeedbackStyles.ERROR_ICON_COLOR),
                    ft.Text(value=translation.get("error")),
                ]
            ),
        )
