import flet as ft


class UserView(ft.Card):
    def __init__(self, texts: dict[str, str]) -> None:
        super().__init__(
            content=ft.Container(
                content=ft.Text("User"),
                alignment=ft.alignment.center,
                expand=True,
            )
        )
