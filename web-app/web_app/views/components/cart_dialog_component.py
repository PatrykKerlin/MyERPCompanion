from collections.abc import Callable

import flet as ft
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class CartDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        cart_content: ft.Control,
        on_continue_clicked: Callable[[ft.Event[ft.TextButton]], ft.DialogControl | None],
        on_proceed_clicked: Callable[[ft.Event[ft.Button]], ft.DialogControl | None],
    ) -> None:
        continue_button = self._get_text_button(
            content=translation.get("continue_shopping"),
            on_click=on_continue_clicked,
            style=ButtonStyles.regular,
        )
        proceed_button = self._get_button(
            content=translation.get("proceed_to_checkout"),
            on_click=on_proceed_clicked,
            style=ButtonStyles.primary_regular,
        )
        super().__init__(
            title=translation.get("cart"),
            controls=[cart_content],
            actions=[continue_button, proceed_button],
        )
        self.continue_button = continue_button
        self.proceed_button = proceed_button
