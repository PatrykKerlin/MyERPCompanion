import flet as ft


class GroupView(ft.Container):
    def __init__(self) -> None:
        super().__init__(
            content=ft.Text("Group", size=20),
            alignment=ft.alignment.center,
            expand=True,
        )
