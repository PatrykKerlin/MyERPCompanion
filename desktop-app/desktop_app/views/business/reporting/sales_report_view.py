from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import TYPE_CHECKING, cast

import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles, DialogStyles
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.reporting.sales_report_controller import SalesReportController


class SalesReportView(BaseView):
    def __init__(
        self,
        controller: SalesReportController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        totals: dict[str, str],
        date_from: date | None,
        date_to: date | None,
        first_sales_date: date | None,
        currency_options: list[tuple[int, str]],
        customer_options: list[tuple[int, str]],
        item_options: list[tuple[int, str]],
        category_options: list[tuple[int, str]],
        currency_id: int | None,
        customer_id: int | None,
        item_id: int | None,
        category_id: int | None,
        category_chart: bytes | None,
        daily_chart: bytes | None,
        category_chart_dialog: bytes | None,
        daily_chart_dialog: bytes | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None
        self._master_column.spacing = AppDimensions.SPACE_2XL

        self.__totals = dict(totals)
        self.__category_chart = category_chart
        self.__daily_chart = daily_chart
        self.__category_chart_dialog = category_chart_dialog
        self.__daily_chart_dialog = daily_chart_dialog
        self.__slider_min_date, self.__slider_max_date = self.__resolve_slider_bounds(first_sales_date)
        self.__slider_max_offset = max(
            self.__to_month_index(self.__slider_max_date) - self.__to_month_index(self.__slider_min_date),
            1,
        )
        self.__date_from_value, self.__date_to_value = self.__normalize_initial_range(date_from, date_to)
        self.__date_range_input = ft.RangeSlider(
            min=0,
            max=self.__slider_max_offset,
            round=0,
            start_value=self.__to_slider_offset(self.__date_from_value) if self.__date_from_value is not None else 0,
            end_value=(
                self.__to_slider_offset(self.__date_to_value)
                if self.__date_to_value is not None
                else self.__slider_max_offset
            ),
            on_change=self.__on_date_range_changed,
            expand=True,
        )
        self.__date_range_styled = ft.Container(
            content=self.__date_range_input,
            theme=ft.Theme(
                slider_theme=ft.SliderTheme(
                    value_indicator_color=ft.Colors.TRANSPARENT,
                    value_indicator_stroke_color=ft.Colors.TRANSPARENT,
                    value_indicator_text_style=ft.TextStyle(color=ft.Colors.TRANSPARENT),
                )
            ),
        )
        self.__date_range_text = ft.Text(no_wrap=False, max_lines=2)
        self.__update_date_range_text()

        currency_container, _ = self._get_dropdown("currency_id", 2, currency_options)
        self.__currency_input = cast(ft.Dropdown, currency_container.content)
        self.__currency_input.label = self._translation.get("currency")
        self.__currency_input.value = str(currency_id) if currency_id is not None else "0"

        customer_container, _ = self._get_dropdown("customer_id", 2, customer_options)
        self.__customer_input = cast(ft.Dropdown, customer_container.content)
        self.__customer_input.label = self._translation.get("customer")
        self.__customer_input.value = str(customer_id) if customer_id is not None else "0"

        item_container, _ = self._get_dropdown("item_id", 2, item_options)
        self.__item_input = cast(ft.Dropdown, item_container.content)
        self.__item_input.label = self._translation.get("item")
        self.__item_input.value = str(item_id) if item_id is not None else "0"

        category_container, _ = self._get_dropdown("category_id", 2, category_options)
        self.__category_input = cast(ft.Dropdown, category_container.content)
        self.__category_input.label = self._translation.get("category")
        self.__category_input.value = str(category_id) if category_id is not None else "0"
        self._inputs.update(
            {
                "currency_id": FieldGroup(input=(currency_container, 0)),
                "customer_id": FieldGroup(input=(customer_container, 0)),
                "item_id": FieldGroup(input=(item_container, 0)),
                "category_id": FieldGroup(input=(category_container, 0)),
            }
        )

        self.__totals_row = ft.ResponsiveRow(
            columns=14,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[],
        )
        self.__category_chart_container = ft.Container(expand=True, alignment=AlignmentStyles.CENTER)
        self.__daily_chart_container = ft.Container(expand=True, alignment=AlignmentStyles.CENTER)

        self.__build_layout()
        self.__render_report()

    def set_report_data(
        self,
        totals: dict[str, str],
        category_chart: bytes | None,
        daily_chart: bytes | None,
        category_chart_dialog: bytes | None,
        daily_chart_dialog: bytes | None,
    ) -> None:
        self.__totals = dict(totals)
        self.__category_chart = category_chart
        self.__daily_chart = daily_chart
        self.__category_chart_dialog = category_chart_dialog
        self.__daily_chart_dialog = daily_chart_dialog
        self.__render_report()

    def reset_filters(self) -> None:
        self.__date_from_value = None
        self.__date_to_value = None
        self.__date_range_input.start_value = 0
        self.__date_range_input.end_value = self.__slider_max_offset
        self.__update_date_range_text()
        self.__currency_input.value = "0"
        self.__customer_input.value = "0"
        self.__item_input.value = "0"
        self.__category_input.value = "0"
        self.safe_update(self.__date_range_input)
        self.safe_update(self.__date_range_text)
        self.safe_update(self.__currency_input)
        self.safe_update(self.__customer_input)
        self.safe_update(self.__item_input)
        self.safe_update(self.__category_input)

    def __build_layout(self) -> None:
        apply_button = ft.Button(
            content=self._translation.get("apply_filters"),
            on_click=lambda _: self._controller.on_apply_filters_clicked(
                date_from=self.__date_from_value,
                date_to=self.__date_to_value,
                currency_id=self.__currency_input.value,
                customer_id=self.__customer_input.value,
                item_id=self.__item_input.value,
                category_id=self.__category_input.value,
            ),
            style=ButtonStyles.primary_regular,
        )
        clear_button = ft.Button(
            content=self._translation.get("clear_filters"),
            on_click=lambda _: self._controller.on_clear_filters_clicked(),
            style=ButtonStyles.regular,
        )

        filters_top_row = ft.ResponsiveRow(
            columns=12,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[
                self.__build_date_range_input(),
                self.__build_filter_input(self._translation.get("currency"), self.__currency_input, md_size=2),
                self.__build_filter_input(self._translation.get("customer"), self.__customer_input, md_size=2),
                self.__build_filter_input(self._translation.get("item"), self.__item_input, md_size=2),
                self.__build_filter_input(self._translation.get("category"), self.__category_input, md_size=2),
            ],
        )
        filters_bottom_row = ft.ResponsiveRow(
            columns=12,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[
                self.__build_date_range_caption(),
                ft.Container(
                    col={"sm": 12, "md": 8},
                    alignment=AlignmentStyles.CENTER_RIGHT,
                    content=ft.Row(
                        controls=[clear_button, apply_button],
                        alignment=AlignmentStyles.AXIS_END,
                    ),
                ),
            ],
        )
        filters = ft.Column(
            spacing=AppDimensions.SPACE_SM,
            controls=[filters_top_row, filters_bottom_row],
        )
        filters_section = ft.Container(
            border=ft.Border.all(1, AppColors.OUTLINE),
            border_radius=AppDimensions.RADIUS_SM,
            padding=ft.Padding.all(AppDimensions.SPACE_SM),
            content=filters,
        )

        charts = ft.Row(
            expand=True,
            spacing=AppDimensions.SPACE_LG,
            controls=[
                ft.Container(
                    expand=1,
                    border=ft.Border.all(1, AppColors.OUTLINE),
                    border_radius=AppDimensions.RADIUS_SM,
                    padding=ft.Padding.all(AppDimensions.SPACE_SM),
                    content=self.__category_chart_container,
                ),
                ft.Container(
                    expand=1,
                    border=ft.Border.all(1, AppColors.OUTLINE),
                    border_radius=AppDimensions.RADIUS_SM,
                    padding=ft.Padding.all(AppDimensions.SPACE_SM),
                    content=self.__daily_chart_container,
                ),
            ],
        )

        self._master_column.controls = [
            filters_section,
            self.__totals_row,
            charts,
        ]
        self.content = ft.Container(
            content=self._master_column,
            expand=True,
            padding=ft.Padding.symmetric(
                horizontal=AppDimensions.PADDING_FORM_HORIZONTAL,
                vertical=AppDimensions.PADDING_FORM_VERTICAL,
            ),
        )

    def __build_filter_input(self, label: str, control: ft.Control, md_size: int = 2) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": md_size},
            content=ft.Column(
                controls=[ft.Text(label), control],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __build_date_range_input(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=ft.Column(
                controls=[
                    ft.Text(f"{self._translation.get('date_from')} / {self._translation.get('date_to')}"),
                    self.__date_range_styled,
                ],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __build_date_range_caption(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=self.__date_range_text,
        )

    def __render_report(self) -> None:
        self.__render_totals()
        self.__render_charts()

    def __render_totals(self) -> None:
        self.__totals_row.controls = [
            self.__build_total_item("orders_count", self.__totals.get("orders_count", "0")),
            self.__build_total_item("rows_count", self.__totals.get("rows_count", "0")),
            self.__build_total_item("total_quantity", self.__totals.get("quantity", "0")),
            self.__build_total_item("total_net", self.__totals.get("total_net", "0.00")),
            self.__build_total_item("total_vat", self.__totals.get("total_vat", "0.00")),
            self.__build_total_item("total_gross", self.__totals.get("total_gross", "0.00")),
            self.__build_total_item("total_discount", self.__totals.get("total_discount", "0.00")),
        ]
        self.safe_update(self.__totals_row)

    def __build_total_item(self, label_key: str, value: str) -> ft.Container:
        return ft.Container(
            col={"sm": 14, "md": 2},
            border=ft.Border.all(1, AppColors.OUTLINE),
            border_radius=AppDimensions.RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=AppDimensions.SPACE_SM, vertical=AppDimensions.SPACE_XS),
            content=ft.Column(
                controls=[
                    ft.Text(self._translation.get(label_key)),
                    ft.Text(value),
                ],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __render_charts(self) -> None:
        self.__category_chart_container.content = self.__build_chart_content(
            self._translation.get("total_net"),
            self.__category_chart,
            self.__category_chart_dialog,
        )
        self.__daily_chart_container.content = self.__build_chart_content(
            self._translation.get("total_quantity"),
            self.__daily_chart,
            self.__daily_chart_dialog,
        )
        self.safe_update(self.__category_chart_container)
        self.safe_update(self.__daily_chart_container)

    def __build_chart_content(self, title: str, chart: bytes | None, dialog_chart: bytes | None) -> ft.Control:
        if not chart:
            image_holder: ft.Control = ft.Container(
                expand=True,
                alignment=AlignmentStyles.CENTER,
                content=ft.Text(self._translation.get("no_chart_data")),
            )
        else:
            image_holder = ft.Container(
                expand=True,
                alignment=AlignmentStyles.CENTER,
                on_click=lambda _, image=(dialog_chart or chart), chart_title=title: self.__open_chart_dialog(
                    image,
                    chart_title,
                ),
                content=ft.Image(src=chart, fit=ft.BoxFit.CONTAIN, expand=True),
            )
        return ft.Column(
            expand=True,
            controls=[
                ft.Text(title, weight=ft.FontWeight.W_600),
                image_holder,
            ],
            spacing=AppDimensions.SPACE_SM,
        )

    def __open_chart_dialog(self, chart: bytes, title: str) -> None:
        if not self.page:
            return
        width = self.__resolve_chart_dialog_width()
        height = self.__resolve_chart_dialog_height()
        dialog = BaseDialog(
            title=ft.Text(title),
            controls=[
                ft.Container(
                    width=width,
                    height=height,
                    alignment=AlignmentStyles.CENTER,
                    content=ft.Image(src=chart, fit=ft.BoxFit.CONTAIN, expand=True),
                )
            ],
            actions=[
                ft.TextButton(
                    self._translation.get("close"),
                    on_click=lambda _: self._controller._page.pop_dialog(),
                    style=ButtonStyles.regular,
                ),
            ],
            scrollable=False,
        )
        self._controller._queue_dialog(dialog)

    def __resolve_chart_dialog_width(self) -> int:
        page_width = int(self.page.width or AppDimensions.DESKTOP_WINDOW_WIDTH) if self.page else AppDimensions.DESKTOP_WINDOW_WIDTH

        horizontal_overhead = 2 * (DialogStyles.INSET_HORIZONTAL + DialogStyles.CONTENT_HORIZONTAL)
        max_width = max(320, page_width - horizontal_overhead)
        width = min(int(page_width * AppDimensions.REPORT_DIALOG_WIDTH_RATIO), max_width)
        return width

    def __resolve_chart_dialog_height(self) -> int:
        page_height = (
            int(self.page.height or AppDimensions.DESKTOP_WINDOW_HEIGHT) if self.page else AppDimensions.DESKTOP_WINDOW_HEIGHT
        )
        vertical_overhead = (
            (2 * DialogStyles.INSET_VERTICAL)
            + DialogStyles.TITLE_TOP
            + DialogStyles.CONTENT_TOP
            + DialogStyles.CONTENT_BOTTOM
            + DialogStyles.ACTIONS_TOP
            + DialogStyles.ACTIONS_BOTTOM
            + AppDimensions.CONTROL_HEIGHT
        )
        max_height = max(1, page_height - vertical_overhead)
        height = min(int(page_height * AppDimensions.REPORT_DIALOG_HEIGHT_RATIO), max_height)
        return height

    def __on_date_range_changed(self, event: ft.Event[ft.RangeSlider]) -> None:
        start_offset = self.__coerce_slider_offset(event.control.start_value)
        end_offset = self.__coerce_slider_offset(event.control.end_value)
        event.control.start_value = start_offset
        event.control.end_value = end_offset
        start_month = self.__from_slider_offset(start_offset)
        end_month = self.__from_slider_offset(end_offset)
        self.__date_from_value = None if start_offset <= 0 else start_month
        self.__date_to_value = None if end_offset >= self.__slider_max_offset else self.__month_end(end_month)
        self.__update_date_range_text()
        self.safe_update(self.__date_range_text)

    def __update_date_range_text(self) -> None:
        from_value = (
            self.__date_from_value.isoformat()
            if self.__date_from_value is not None
            else self.__slider_min_date.isoformat()
        )
        to_value = (
            self.__date_to_value.isoformat()
            if self.__date_to_value is not None
            else self.__month_end(self.__slider_max_date).isoformat()
        )
        self.__date_range_text.value = (
            f"{self._translation.get('date_from')}: {from_value}\n" f"{self._translation.get('date_to')}: {to_value}"
        )

    def __to_slider_offset(self, value: date) -> int:
        offset = self.__to_month_index(self.__month_start(value)) - self.__to_month_index(self.__slider_min_date)
        return max(0, min(offset, self.__slider_max_offset))

    def __from_slider_offset(self, offset: int) -> date:
        base_index = self.__to_month_index(self.__slider_min_date)
        return self.__from_month_index(base_index + offset)

    def __coerce_slider_offset(self, raw_offset: int | float) -> int:
        offset = int(round(raw_offset))
        return max(0, min(offset, self.__slider_max_offset))

    @staticmethod
    def __month_start(value: date) -> date:
        return date(value.year, value.month, 1)

    @staticmethod
    def __month_end(value: date) -> date:
        return date(value.year, value.month, monthrange(value.year, value.month)[1])

    @staticmethod
    def __to_month_index(value: date) -> int:
        return value.year * 12 + (value.month - 1)

    @staticmethod
    def __from_month_index(index: int) -> date:
        return date(index // 12, (index % 12) + 1, 1)

    @staticmethod
    def __resolve_slider_bounds(first_sales_date: date | None) -> tuple[date, date]:
        today = date.today()
        max_date = SalesReportView.__month_start(today)
        min_date = SalesReportView.__month_start(first_sales_date) if first_sales_date is not None else max_date
        if min_date > max_date:
            min_date = max_date
        return min_date, max_date

    def __normalize_initial_range(
        self, date_from: date | None, date_to: date | None
    ) -> tuple[date | None, date | None]:
        range_min = self.__slider_min_date
        range_max = self.__month_end(self.__slider_max_date)
        normalized_from = self.__month_start(date_from) if date_from is not None else None
        normalized_to = self.__month_end(date_to) if date_to is not None else None
        if normalized_from is not None:
            if normalized_from < range_min:
                normalized_from = range_min
            if normalized_from > range_max:
                normalized_from = range_max
        if normalized_to is not None:
            if normalized_to < range_min:
                normalized_to = range_min
            if normalized_to > range_max:
                normalized_to = range_max
        if normalized_from is not None and normalized_to is not None and normalized_from > normalized_to:
            normalized_from = normalized_to
        return normalized_from, normalized_to
