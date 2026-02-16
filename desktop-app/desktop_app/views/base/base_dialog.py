import flet as ft
from styles.styles import AlignmentStyles


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
            alignment=AlignmentStyles.CENTER,
            content=ft.Container(
                content=ft.Column(
                    controls=controls,
                    tight=True,
                    alignment=AlignmentStyles.AXIS_CENTER,
                    horizontal_alignment=AlignmentStyles.CROSS_CENTER,
                ),
            ),
            actions=actions or [],
            title=title,
            scrollable=True,
            **kwargs,
        )
