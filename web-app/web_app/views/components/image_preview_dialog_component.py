from collections.abc import Callable

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class ImagePreviewDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        image_url: str,
        on_ok_clicked: Callable[[ft.Event[ft.TextButton]], ft.DialogControl | None],
    ) -> None:
        super().__init__(
            title=None,
            controls=[
                ft.Image(
                    src=image_url,
                    width=AppDimensions.DIALOG_IMAGE_SIZE,
                    height=AppDimensions.DIALOG_IMAGE_SIZE,
                    fit=ft.BoxFit.CONTAIN,
                )
            ],
            actions=[ft.TextButton(translation.get("ok"), on_click=on_ok_clicked, style=ButtonStyles.regular)],
        )
