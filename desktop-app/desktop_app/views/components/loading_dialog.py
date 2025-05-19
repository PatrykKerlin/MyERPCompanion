import flet as ft
from views.base import BaseDialog


class LoadingDialog(BaseDialog):
    def __init__(self, texts: dict[str, str]) -> None:
        super().__init__(
            texts=texts,
            controls=[ft.Text(texts["loading"])],
            actions=[ft.ProgressBar()],
        )
