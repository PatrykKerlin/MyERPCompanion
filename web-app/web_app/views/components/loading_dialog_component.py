from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import DialogStyles

if TYPE_CHECKING:
    from utils.translation import Translation


class LoadingDialogComponent(ft.AlertDialog):
    def __init__(self, translation: Translation, min_visible_seconds: float = 0.1) -> None:
        self.__min_visible_seconds = max(min_visible_seconds, 0)
        super().__init__(
            modal=DialogStyles.MODAL,
            elevation=DialogStyles.ELEVATION,
            alignment=DialogStyles.ALIGNMENT,
            inset_padding=DialogStyles.INSET_PADDING,
            content_padding=DialogStyles.CONTENT_PADDING,
            scrollable=False,
            content=ft.Container(
                padding=DialogStyles.CONTENT_INNER_PADDING,
                content=ft.Column(
                    controls=[ft.Text(translation.get("loading")), ft.ProgressBar()],
                    tight=True,
                    spacing=DialogStyles.CONTENT_SPACING,
                    alignment=DialogStyles.CONTENT_ALIGNMENT,
                    horizontal_alignment=DialogStyles.CONTENT_HORIZONTAL_ALIGNMENT,
                ),
            ),
        )

    @property
    def min_visible_seconds(self) -> float:
        return self.__min_visible_seconds
