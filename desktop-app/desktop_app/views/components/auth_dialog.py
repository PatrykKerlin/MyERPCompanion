import flet as ft
from views.base import BaseDialog
from collections.abc import Callable
from styles import ButtonStyles


class AuthDialog(BaseDialog):
    def __init__(
        self, texts: dict[str, str], on_cancel: Callable[[], None], on_login: Callable[[str, str], None]
    ) -> None:
        login_field = ft.TextField(label=texts["login"], autofocus=True)
        password_field = ft.TextField(label=texts["password"], password=True, can_reveal_password=True)
        login_button = ft.ElevatedButton(
            text=texts["log_in"],
            on_click=lambda _: on_login(
                login_field.value or "",
                password_field.value or "",
            ),
            style=ButtonStyles.small_padding,
        )
        cancel_button = ft.TextButton(
            texts["cancel"],
            on_click=lambda _: on_cancel(),
            style=ButtonStyles.small_padding,
        )

        super().__init__(
            texts=texts,
            controls=[login_field, password_field],
            actions=[cancel_button, login_button],
            title=texts["login"],
        )
