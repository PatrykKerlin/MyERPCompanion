from typing import Sequence

import flet as ft


class BaseDialog(ft.AlertDialog):
    def __init__(
        self,
        controls: Sequence[ft.Control],
        actions: Sequence[ft.Control] = [],
        title: str | ft.Control | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            modal=True,
            alignment=ft.alignment.center,
            content=ft.Container(
                content=ft.Column(
                    controls=list(controls),
                    tight=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            actions=list(actions),
            title=title,
            **kwargs,
        )
