import flet as ft
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class CheckoutDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        controls: list[ft.Control],
        back_button: ft.TextButton,
        confirm_button: ft.Button,
    ) -> None:
        super().__init__(
            title=translation.get("checkout"),
            controls=controls,
            actions=[back_button, confirm_button],
        )
        dialog_content = self.content
        if isinstance(dialog_content, ft.Container) and isinstance(dialog_content.content, ft.Column):
            dialog_content.content.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    def set_content_width(self, width: int) -> None:
        dialog_content = self.content
        if isinstance(dialog_content, ft.Container):
            dialog_content.width = width
