from collections.abc import Callable

import flet as ft
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class MessageDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        message_key: str,
        on_ok_clicked: Callable[[ft.Event[ft.Button]], ft.DialogControl | None],
    ) -> None:
        super().__init__(
            controls=[self._get_label(translation.get(message_key))],
            actions=[
                self._get_button(
                    content=translation.get("ok"), on_click=on_ok_clicked, style=ButtonStyles.primary_regular
                )
            ],
        )
