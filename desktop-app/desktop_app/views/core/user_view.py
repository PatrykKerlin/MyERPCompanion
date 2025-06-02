import flet as ft


class UserView(ft.Card):
    def __init__(self) -> None:
        super().__init__(
            content=ft.Container(
                content=ft.Text("User", size=20),
                alignment=ft.alignment.center,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                expand=True,
            )
        )
