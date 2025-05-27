from typing import Sequence

import flet as ft


class BaseDialog(ft.AlertDialog):
    def __init__(
        self, texts: dict[str, str], controls: Sequence[ft.Control], actions: Sequence[ft.Control] = [], **kwargs
    ) -> None:
        self._texts = texts
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
            **kwargs,
        )
