import flet as ft

from views.base.base_dialog import BaseDialog


class LoadingDialogComponent(BaseDialog):
    def __init__(self, translation: dict[str, str]) -> None:
        super().__init__(
            controls=[ft.Text(translation["loading"])],
            actions=[ft.ProgressBar()],
        )
