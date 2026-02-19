import flet as ft
from styles.styles import BaseDialogStyles


class BaseDialog(ft.AlertDialog):
    def __init__(
        self,
        controls: list[ft.Control],
        actions: list[ft.Control] | None = None,
        title: str | ft.Control | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            modal=BaseDialogStyles.MODAL,
            alignment=BaseDialogStyles.ALIGNMENT,
            content=ft.Container(
                content=ft.Column(
                    controls=controls,
                    tight=BaseDialogStyles.CONTENT_TIGHT,
                    alignment=BaseDialogStyles.CONTENT_ALIGNMENT,
                    horizontal_alignment=BaseDialogStyles.CONTENT_HORIZONTAL_ALIGNMENT,
                ),
            ),
            actions=actions or [],
            title=title,
            scrollable=BaseDialogStyles.SCROLLABLE,
            **kwargs,
        )
