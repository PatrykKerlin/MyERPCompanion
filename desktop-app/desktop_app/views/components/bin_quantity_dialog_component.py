import asyncio

import flet as ft
from styles import AppColors, ButtonStyles, ControlStyles
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.controls.numeric_field_control import NumericField


class BinQuantityDialogComponent(BaseDialog):
    def __init__(
        self,
        translation: Translation,
        bin_options: list[tuple[int, str, int]],
        default_quantity: int,
        max_total: int,
    ) -> None:
        self.__future: asyncio.Future[tuple[int, int] | None] = asyncio.get_running_loop().create_future()
        self.__bin_map = {str(bin_id): max(quantity, 0) for bin_id, _, quantity in bin_options}
        self.__max_total = max(max_total, 0)
        self.__default_quantity = max(default_quantity, 1)
        sorted_bins = sorted(bin_options, key=lambda item: item[1])
        options = [ft.dropdown.Option(key=str(bin_id), text=label) for bin_id, label, _ in sorted_bins]
        initial_key = options[0].key if options and options[0].key is not None else "0"
        self.__bin_dropdown = ft.Dropdown(
            options=options,
            value=initial_key,
            expand=True,
            on_select=self.__on_bin_changed,
            editable=True,
            enable_search=True,
            enable_filter=True,
        )
        self.__bin_dropdown.border_radius = ControlStyles.DROPDOWN_BORDER_RADIUS
        self.__bin_dropdown.border_color = ControlStyles.DROPDOWN_BORDER_COLOR
        self.__bin_dropdown.focused_border_color = ControlStyles.DROPDOWN_FOCUSED_BORDER_COLOR
        self.__bin_dropdown.content_padding = ControlStyles.DROPDOWN_PADDING
        max_value = min(self.__bin_map.get(initial_key, 0), self.__max_total)
        self.__quantity_field = NumericField(
            value=min(max_value, self.__default_quantity),
            min_value=1,
            max_value=max_value,
            step=1,
            read_only=False,
        )
        cancel_button = ft.Button(
            content=translation.get("cancel"),
            on_click=lambda _: self.__set_result(None),
            style=ButtonStyles.compact,
        )
        confirm_button = ft.Button(
            content=translation.get("ok"),
            on_click=lambda _: self.__set_result(self.__read_values()),
            style=ButtonStyles.primary_compact,
        )
        super().__init__(
            controls=[
                ft.Text(translation.get("source_bin")),
                self.__bin_dropdown,
                ft.Text(translation.get("quantity")),
                self.__quantity_field,
            ],
            actions=[cancel_button, confirm_button],
            title=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.CONFIRMATION_NUMBER, color=AppColors.PRIMARY),
                    ft.Text(value=translation.get("confirm")),
                ]
            ),
        )

    @property
    def future(self) -> asyncio.Future[tuple[int, int] | None]:
        return self.__future

    def __on_bin_changed(self, event: ft.Event[ft.Dropdown]) -> None:
        key = event.control.value or "0"
        max_value = min(self.__bin_map.get(key, 0), self.__max_total)
        self.__quantity_field.set_limits(1, max_value)
        self.__quantity_field.value = min(max_value, self.__default_quantity)
        self.__quantity_field.update()

    def __read_values(self) -> tuple[int, int]:
        bin_value = self.__bin_dropdown.value or "0"
        max_value = min(self.__bin_map.get(bin_value, 0), self.__max_total)
        quantity = int(self.__quantity_field.value or 0)
        quantity = min(quantity, max_value)
        return int(bin_value), quantity

    def __set_result(self, result: tuple[int, int] | None) -> None:
        if not self.__future.done():
            self.__future.set_result(result)
