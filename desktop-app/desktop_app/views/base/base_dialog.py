import flet as ft


class BaseDialog(ft.AlertDialog):
    def __init__(
        self,
        controls: list[ft.Control],
        actions: list[ft.Control] | None = None,
        title: str | ft.Control | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            modal=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                content=ft.Column(
                    controls=controls,
                    tight=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            actions=actions or [],
            title=title,
            scrollable=True,
            **kwargs,
        )
