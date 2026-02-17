import asyncio

import flet as ft
from styles.colors import AppColors
from styles.styles import ButtonStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.controls.numeric_field_control import NumericField


class QuantityDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        max_value: int,
        default_value: int | None = None,
        min_value: int = 1,
        step: int = 1,
    ) -> None:
        self.__future: asyncio.Future[int | None] = asyncio.get_running_loop().create_future()
        self.__step = max(step, 1)
        resolved_default = max_value if default_value is None else default_value
        self.__quantity_field = NumericField(
            value=resolved_default,
            min_value=min_value,
            max_value=max_value,
            step=self.__step,
            read_only=False,
        )
        cancel_button = ft.Button(
            content=translation.get("cancel"),
            on_click=lambda _: self.__set_result(None),
            style=ButtonStyles.regular,
        )
        confirm_button = ft.Button(
            content=translation.get("ok"),
            on_click=lambda _: self.__set_result(self.__read_quantity()),
            style=ButtonStyles.primary_compact,
        )
        label = f"{translation.get('quantity')} ({min_value}-{max_value})"
        super().__init__(
            controls=[ft.Text(label), self.__quantity_field],
            actions=[cancel_button, confirm_button],
            title=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.CONFIRMATION_NUMBER, color=AppColors.PRIMARY),
                    ft.Text(value=translation.get("confirm")),
                ]
            ),
        )

    @property
    def future(self) -> asyncio.Future[int | None]:
        return self.__future

    def __read_quantity(self) -> int:
        value = self.__quantity_field.value
        if value is None:
            return 0
        resolved = int(value)
        if self.__step > 1:
            resolved = (resolved // self.__step) * self.__step
        return resolved

    def __set_result(self, result: int | None) -> None:
        if not self.__future.done():
            self.__future.set_result(result)
