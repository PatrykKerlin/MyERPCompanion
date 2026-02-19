import flet as ft
from styles.styles import DialogStyles


class BaseDialog(ft.AlertDialog):
    def __init__(
        self,
        controls: list[ft.Control],
        actions: list[ft.Control] | None = None,
        title: str | ft.Control | None = None,
    ) -> None:
        super().__init__(
            modal=DialogStyles.MODAL,
            title=title,
            content=ft.Container(
                padding=DialogStyles.CONTENT_INNER_PADDING,
                content=ft.Column(
                    controls=controls,
                    tight=True,
                    spacing=DialogStyles.CONTENT_SPACING,
                    alignment=DialogStyles.CONTENT_ALIGNMENT,
                    horizontal_alignment=DialogStyles.CONTENT_HORIZONTAL_ALIGNMENT,
                ),
            ),
            actions=actions or [],
            elevation=DialogStyles.ELEVATION,
            title_padding=DialogStyles.TITLE_PADDING,
            content_padding=DialogStyles.CONTENT_PADDING,
            actions_padding=DialogStyles.ACTIONS_PADDING,
            actions_alignment=DialogStyles.ACTIONS_ALIGNMENT,
            action_button_padding=DialogStyles.ACTION_BUTTON_PADDING,
            actions_overflow_button_spacing=DialogStyles.ACTIONS_OVERFLOW_BUTTON_SPACING,
            inset_padding=DialogStyles.INSET_PADDING,
            alignment=DialogStyles.ALIGNMENT,
            scrollable=DialogStyles.SCROLLABLE,
        )
