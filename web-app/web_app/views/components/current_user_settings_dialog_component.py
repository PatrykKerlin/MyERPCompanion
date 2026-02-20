from collections.abc import Callable, Sequence

import flet as ft
from styles.styles import ButtonStyles, CurrentUserSettingsDialogStyles, DialogStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog


class CurrentUserSettingsDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        language_options: Sequence[tuple[int | str, str]],
        language_value: str,
        theme_value: str,
        on_cancel_clicked: Callable[[ft.Event[ft.Button]], ft.DialogControl | None],
        on_save_clicked: Callable[[ft.Event[ft.Button]], ft.DialogControl | None],
    ) -> None:
        self.__password_field = self._get_text_field(password=True, expand=True)
        self.__password_repeat_field = self._get_text_field(password=True, expand=True)
        self.__language_dropdown = self._get_dropdown(
            options=language_options,
            value=language_value,
            include_empty_option=False,
            expand=True,
        )
        self.__theme_dropdown = self._get_dropdown(
            options=[
                ("system", translation.get("system")),
                ("dark", translation.get("dark")),
                ("light", translation.get("light")),
            ],
            value=theme_value,
            include_empty_option=False,
            editable=False,
            enable_search=False,
            enable_filter=False,
            expand=True,
        )

        save_button = self._get_button(
            content=translation.get("save"), on_click=on_save_clicked, style=ButtonStyles.primary_regular
        )
        cancel_button = self._get_button(
            content=translation.get("cancel"),
            on_click=on_cancel_clicked,
            style=ButtonStyles.regular,
        )

        controls: list[ft.Control] = [
            ft.Container(
                content=self.__build_labeled_control(translation.get("password"), self.__password_field),
                padding=CurrentUserSettingsDialogStyles.FIELD_BOTTOM_PADDING,
            ),
            ft.Container(
                content=self.__build_labeled_control(translation.get("password_repeat"), self.__password_repeat_field),
                padding=CurrentUserSettingsDialogStyles.FIELD_BOTTOM_PADDING,
            ),
            ft.Container(
                content=self.__build_labeled_control(translation.get("language_id"), self.__language_dropdown),
                padding=CurrentUserSettingsDialogStyles.FIELD_BOTTOM_PADDING,
            ),
            ft.Container(content=self.__build_labeled_control(translation.get("theme"), self.__theme_dropdown)),
        ]

        super().__init__(
            title=translation.get("current_user"),
            controls=controls,
            actions=[cancel_button, save_button],
        )

        dialog_content = self.content
        if isinstance(dialog_content, ft.Container):
            dialog_content.width = DialogStyles.CURRENT_USER_SETTINGS_CONTENT_WIDTH
            dialog_content.alignment = ft.Alignment.TOP_LEFT
            content_column = dialog_content.content
            if isinstance(content_column, ft.Column):
                content_column.alignment = ft.MainAxisAlignment.START
                content_column.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    @property
    def password_value(self) -> str | None:
        return self.__password_field.value

    @property
    def password_repeat_value(self) -> str | None:
        return self.__password_repeat_field.value

    @property
    def language_value(self) -> str | None:
        return self.__language_dropdown.value

    @property
    def theme_value(self) -> str | None:
        return self.__theme_dropdown.value

    def __build_labeled_control(self, label: str, control: ft.Control) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            columns=CurrentUserSettingsDialogStyles.ROW_COLUMNS,
            alignment=CurrentUserSettingsDialogStyles.ROW_ALIGNMENT,
            vertical_alignment=CurrentUserSettingsDialogStyles.ROW_VERTICAL_ALIGNMENT,
            spacing=CurrentUserSettingsDialogStyles.ROW_SPACING,
            controls=[
                ft.Container(col=CurrentUserSettingsDialogStyles.LABEL_COL, content=self._get_label(label, colon=True)),
                ft.Container(col=CurrentUserSettingsDialogStyles.CONTROL_COL, content=control),
            ],
        )
