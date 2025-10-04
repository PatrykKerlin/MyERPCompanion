from __future__ import annotations

from typing import TYPE_CHECKING
import flet as ft

from views.base.base_dialog import BaseDialog

if TYPE_CHECKING:
    from utils.translation import Translation


class LoadingDialogComponent(BaseDialog):
    def __init__(self, translation: Translation) -> None:
        super().__init__(
            controls=[ft.Text(translation.get("loading"))],
            actions=[ft.ProgressBar()],
        )
