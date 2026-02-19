from collections.abc import Callable

import flet as ft
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class OrderConfirmationDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        order_number: str,
        on_ok_clicked: Callable[[ft.Event[ft.TextButton]], ft.DialogControl | None],
    ) -> None:
        super().__init__(
            title=translation.get("checkout"),
            controls=[ft.Text(translation.get("order_created").format(order_number=order_number))],
            actions=[
                ft.TextButton(
                    translation.get("ok"),
                    on_click=on_ok_clicked,
                    style=ButtonStyles.regular,
                )
            ],
        )
