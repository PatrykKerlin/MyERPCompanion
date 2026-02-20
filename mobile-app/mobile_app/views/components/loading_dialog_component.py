from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from views.base.base_dialog import BaseDialog

if TYPE_CHECKING:
    from utils.translation import Translation


class LoadingDialogComponent(BaseDialog):
    def __init__(self, translation: Translation, min_visible_seconds: float = 0.1) -> None:
        self.__min_visible_seconds = max(min_visible_seconds, 0)
        super().__init__(
            controls=[self._get_label(translation.get("loading"))],
            actions=[ft.ProgressBar()],
        )

    @property
    def min_visible_seconds(self) -> float:
        return self.__min_visible_seconds
