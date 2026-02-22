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
            content=ft.Container(
                content=ft.Column(
                    controls=[ft.Text(translation.get("loading")), ft.ProgressBar()],
                    tight=True,
                    spacing=DialogStyles.CONTENT_SPACING,
                    alignment=DialogStyles.CONTENT_ALIGNMENT,
                    horizontal_alignment=DialogStyles.CONTENT_HORIZONTAL_ALIGNMENT,
                ),
            ),
            actions=[],
            elevation=DialogStyles.ELEVATION,
            content_padding=DialogStyles.CONTENT_PADDING,
            actions_padding=DialogStyles.LOADING_ACTIONS_PADDING,
            actions_alignment=DialogStyles.ACTIONS_ALIGNMENT,
            action_button_padding=DialogStyles.LOADING_ACTION_BUTTON_PADDING,
            actions_overflow_button_spacing=DialogStyles.LOADING_ACTIONS_OVERFLOW_BUTTON_SPACING,
            inset_padding=DialogStyles.INSET_PADDING,
            alignment=DialogStyles.ALIGNMENT,
            scrollable=DialogStyles.LOADING_SCROLLABLE,
        )

    @property
    def min_visible_seconds(self) -> float:
        return self.__min_visible_seconds
