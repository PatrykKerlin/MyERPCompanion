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
    from controllers.business.reporting.sales_forecast_report_controller import SalesForecastReportController


class SalesForecastReportView(BaseView):
    def __init__(
        self,  # NOSONAR
        controller: SalesForecastReportController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        totals: dict[str, str],
        date_from: date | None,
        date_to: date | None,
        first_predicted_date: date | None,
        last_predicted_date: date | None,
        currency_options: list[tuple[int, str]],
        customer_options: list[tuple[int, str]],
        item_options: list[tuple[int, str]],
        category_options: list[tuple[int, str]],
        discount_options: list[tuple[str, str]],
        currency_id: int | None,
        customer_id: int | None,
        item_id: int | None,
        category_id: int | None,
        discount_from_key: str,
        discount_to_key: str,
        net_monthly_chart: bytes | None,
        quantity_monthly_chart: bytes | None,
        net_monthly_chart_dialog: bytes | None,
        quantity_monthly_chart_dialog: bytes | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None
        self._master_column.spacing = AppDimensions.SPACE_2XL

        self.__totals = dict(totals)
        self.__net_monthly_chart = net_monthly_chart
        self.__quantity_monthly_chart = quantity_monthly_chart
        self.__net_monthly_chart_dialog = net_monthly_chart_dialog
        self.__quantity_monthly_chart_dialog = quantity_monthly_chart_dialog

        self.__date_slider_min_date, self.__date_slider_max_date = self.__resolve_date_slider_bounds(
            first_predicted_date,
            last_predicted_date,
            date_from,
            date_to,
        )
        self.__date_slider_max_offset = max(
            self.__to_month_index(self.__date_slider_max_date) - self.__to_month_index(self.__date_slider_min_date),
            1,
        )
        self.__date_from_value, self.__date_to_value = self.__normalize_initial_date_range(date_from, date_to)
        self.__date_range_input = ft.RangeSlider(
            min=0,
            max=self.__date_slider_max_offset,
            round=0,
            start_value=self.__to_date_offset(self.__date_from_value) if self.__date_from_value is not None else 0,
            end_value=(
                self.__to_date_offset(self.__date_to_value)
                if self.__date_to_value is not None
                else self.__date_slider_max_offset
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

        self.__discount_steps = self.__resolve_discount_steps(discount_options)
        self.__discount_slider_max_offset = max(len(self.__discount_steps) - 1, 1)
        self.__discount_from_value, self.__discount_to_value = self.__normalize_initial_discount_range(
            discount_from_key,
            discount_to_key,
        )
        self.__discount_from_filter_key: str | None = None
        self.__discount_to_filter_key: str | None = None
        self.__sync_discount_filter_keys()
        self.__discount_range_input = ft.RangeSlider(
            min=0,
            max=self.__discount_slider_max_offset,
            round=0,
            start_value=(
                self.__to_discount_offset(self.__discount_from_value) if self.__discount_from_value is not None else 0
            ),
            end_value=(
                self.__to_discount_offset(self.__discount_to_value)
                if self.__discount_to_value is not None
                else self.__discount_slider_max_offset
            ),
            on_change=self.__on_discount_range_changed,
            expand=True,
        )
        self.__discount_range_styled = ft.Container(
            content=self.__discount_range_input,
            theme=ft.Theme(
                slider_theme=ft.SliderTheme(
                    value_indicator_color=ft.Colors.TRANSPARENT,
                    value_indicator_stroke_color=ft.Colors.TRANSPARENT,
                    value_indicator_text_style=ft.TextStyle(color=ft.Colors.TRANSPARENT),
                )
            ),
        )
        self.__discount_range_text = ft.Text(no_wrap=False, max_lines=2)
        self.__update_discount_range_text()

        currency_container, _ = self._get_dropdown(
            "currency_id",
            2,
            currency_options,
            label=self._translation.get("currency"),
            value=currency_id,
        )
        self.__currency_input = cast(ft.Dropdown, currency_container.content)

        customer_container, _ = self._get_dropdown(
            "customer_id",
            2,
            customer_options,
            label=self._translation.get("customer"),
            value=customer_id,
        )
        self.__customer_input = cast(ft.Dropdown, customer_container.content)

        item_container, _ = self._get_dropdown(
            "item_id",
            2,
            item_options,
            label=self._translation.get("item"),
            value=item_id,
        )
        self.__item_input = cast(ft.Dropdown, item_container.content)

        category_container, _ = self._get_dropdown(
            "category_id",
            2,
            category_options,
            label=self._translation.get("category"),
            value=category_id,
        )
        self.__category_input = cast(ft.Dropdown, category_container.content)

        self._inputs.update(
            {
                "currency_id": FieldGroup(input=(currency_container, 0)),
                "customer_id": FieldGroup(input=(customer_container, 0)),
                "item_id": FieldGroup(input=(item_container, 0)),
                "category_id": FieldGroup(input=(category_container, 0)),
            }
        )

        self.__totals_row = ft.ResponsiveRow(
            columns=12,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[],
        )
        self.__monthly_chart_container = ft.Container(expand=True, alignment=AlignmentStyles.CENTER)
        self.__quantity_chart_container = ft.Container(expand=True, alignment=AlignmentStyles.CENTER)

        self.__build_layout()
        self.__render_report()

    def set_report_data(
        self,
        totals: dict[str, str],
        net_monthly_chart: bytes | None,
        quantity_monthly_chart: bytes | None,
        net_monthly_chart_dialog: bytes | None,
        quantity_monthly_chart_dialog: bytes | None,
    ) -> None:
        self.__totals = dict(totals)
        self.__net_monthly_chart = net_monthly_chart
        self.__quantity_monthly_chart = quantity_monthly_chart
        self.__net_monthly_chart_dialog = net_monthly_chart_dialog
        self.__quantity_monthly_chart_dialog = quantity_monthly_chart_dialog
        self.__render_report()

    def reset_filters(self) -> None:
        self.__date_from_value = None
        self.__date_to_value = None
        self.__date_range_input.start_value = 0
        self.__date_range_input.end_value = self.__date_slider_max_offset
        self.__update_date_range_text()

        self.__discount_from_value = None
        self.__discount_to_value = None
        self.__sync_discount_filter_keys()
        self.__discount_range_input.start_value = 0
        self.__discount_range_input.end_value = self.__discount_slider_max_offset
        self.__update_discount_range_text()

        self.__currency_input.value = "0"
        self.__customer_input.value = "0"
        self.__item_input.value = "0"
        self.__category_input.value = "0"

        self.safe_update(self.__date_range_input)
        self.safe_update(self.__date_range_text)
        self.safe_update(self.__discount_range_input)
        self.safe_update(self.__discount_range_text)
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
                discount_from=self.__discount_from_filter_key,
                discount_to=self.__discount_to_filter_key,
            ),
            style=ButtonStyles.primary_regular,
        )
        clear_button = ft.Button(
            content=self._translation.get("clear_filters"),
            on_click=lambda _: self._controller.on_clear_filters_clicked(),
            style=ButtonStyles.regular,
        )

        filters_top_row = ft.ResponsiveRow(
            columns=14,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[
                self.__build_date_range_input(),
                self.__build_discount_range_input(),
                self.__build_filter_input(self._translation.get("currency"), self.__currency_input),
                self.__build_filter_input(self._translation.get("customer"), self.__customer_input),
                self.__build_filter_input(self._translation.get("category"), self.__category_input),
                self.__build_filter_input(self._translation.get("item"), self.__item_input),
            ],
        )
        filters_bottom_row = ft.ResponsiveRow(
            columns=14,
            spacing=AppDimensions.SPACE_SM,
            run_spacing=AppDimensions.SPACE_SM,
            controls=[
                self.__build_date_range_caption(),
                self.__build_discount_range_caption(),
                ft.Container(
                    col={"sm": 14, "md": 8},
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
                    content=self.__monthly_chart_container,
                ),
                ft.Container(
                    expand=1,
                    border=ft.Border.all(1, AppColors.OUTLINE),
                    border_radius=AppDimensions.RADIUS_SM,
                    padding=ft.Padding.all(AppDimensions.SPACE_SM),
                    content=self.__quantity_chart_container,
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

    def __build_filter_input(self, label: str, control: ft.Control) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 2},
            content=ft.Column(
                controls=[ft.Text(label), control],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __build_date_range_input(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
            content=ft.Column(
                controls=[
                    ft.Text(self._translation.get("date_from")),
                    self.__date_range_styled,
                ],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __build_discount_range_input(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
            content=ft.Column(
                controls=[
                    ft.Text(self._translation.get("discount_from")),
                    self.__discount_range_styled,
                ],
                spacing=AppDimensions.SPACE_2XS,
            ),
        )

    def __build_date_range_caption(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
            content=self.__date_range_text,
        )

    def __build_discount_range_caption(self) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
            content=self.__discount_range_text,
        )

    def __render_report(self) -> None:
        self.__render_totals()
        self.__render_charts()

    def __render_totals(self) -> None:
        self.__totals_row.controls = [
            self.__build_total_item("rows_count", self.__totals.get("rows_count", "0")),
            self.__build_total_item("periods_count", self.__totals.get("periods_count", "0")),
            self.__build_total_item("total_predicted_net", self.__totals.get("total_predicted_net", "0")),
            self.__build_total_item("total_predicted_quantity", self.__totals.get("total_predicted_quantity", "0")),
        ]
        self.safe_update(self.__totals_row)

    def __build_total_item(self, label_key: str, value: str) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
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
        self.__monthly_chart_container.content = self.__build_chart_content(
            self._translation.get("predicted_net_by_month"),
            self.__net_monthly_chart,
            self.__net_monthly_chart_dialog,
        )
        self.__quantity_chart_container.content = self.__build_chart_content(
            self._translation.get("pred_qty_by_month"),
            self.__quantity_monthly_chart,
            self.__quantity_monthly_chart_dialog,
        )
        self.safe_update(self.__monthly_chart_container)
        self.safe_update(self.__quantity_chart_container)

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
                    on_click=lambda _: self.pop_dialog(),
                    style=ButtonStyles.regular,
                )
            ],
            scrollable=False,
        )
        self.queue_dialog(dialog)

    def __resolve_chart_dialog_width(self) -> int:
        page_width = (
            int(self.page.width or AppDimensions.DESKTOP_WINDOW_WIDTH)
            if self.page
            else AppDimensions.DESKTOP_WINDOW_WIDTH
        )

        horizontal_overhead = 2 * (DialogStyles.INSET_HORIZONTAL + DialogStyles.CONTENT_HORIZONTAL)
        max_width = max(320, page_width - horizontal_overhead)
        width = min(int(page_width * AppDimensions.REPORT_DIALOG_WIDTH_RATIO), max_width)
        return width

    def __resolve_chart_dialog_height(self) -> int:
        page_height = (
            int(self.page.height or AppDimensions.DESKTOP_WINDOW_HEIGHT)
            if self.page
            else AppDimensions.DESKTOP_WINDOW_HEIGHT
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
        start_offset = self.__coerce_date_offset(event.control.start_value)
        end_offset = self.__coerce_date_offset(event.control.end_value)
        event.control.start_value = start_offset
        event.control.end_value = end_offset
        start_month = self.__from_date_offset(start_offset)
        end_month = self.__from_date_offset(end_offset)
        self.__date_from_value = None if start_offset <= 0 else start_month
        self.__date_to_value = None if end_offset >= self.__date_slider_max_offset else self.__month_end(end_month)
        self.__update_date_range_text()
        self.safe_update(self.__date_range_text)

    def __update_date_range_text(self) -> None:
        from_value = (
            self.__date_from_value.isoformat()
            if self.__date_from_value is not None
            else self.__date_slider_min_date.isoformat()
        )
        to_value = (
            self.__date_to_value.isoformat()
            if self.__date_to_value is not None
            else self.__month_end(self.__date_slider_max_date).isoformat()
        )
        self.__date_range_text.value = (
            f"{self._translation.get('date_from')}: {from_value}\n{self._translation.get('date_to')}: {to_value}"
        )

    def __to_date_offset(self, value: date) -> int:
        offset = self.__to_month_index(self.__month_start(value)) - self.__to_month_index(self.__date_slider_min_date)
        return max(0, min(offset, self.__date_slider_max_offset))

    def __from_date_offset(self, offset: int) -> date:
        base_index = self.__to_month_index(self.__date_slider_min_date)
        return self.__from_month_index(base_index + offset)

    def __coerce_date_offset(self, raw_offset: int | float) -> int:
        offset = int(round(raw_offset))
        return max(0, min(offset, self.__date_slider_max_offset))

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
    def __resolve_date_slider_bounds(
        first_predicted_date: date | None,
        last_predicted_date: date | None,
        selected_date_from: date | None,
        selected_date_to: date | None,
    ) -> tuple[date, date]:
        default_date = SalesForecastReportView.__month_start(date.today())
        min_date = first_predicted_date or selected_date_from or selected_date_to or default_date
        max_date = last_predicted_date or selected_date_to or selected_date_from or min_date
        normalized_min = SalesForecastReportView.__month_start(min_date)
        normalized_max = SalesForecastReportView.__month_start(max_date)
        if normalized_min > normalized_max:
            normalized_min = normalized_max
        return normalized_min, normalized_max

    def __normalize_initial_date_range(
        self,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[date | None, date | None]:
        range_min = self.__date_slider_min_date
        range_max = self.__month_end(self.__date_slider_max_date)
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

    def __on_discount_range_changed(self, event: ft.Event[ft.RangeSlider]) -> None:
        start_offset = self.__coerce_discount_offset(event.control.start_value)
        end_offset = self.__coerce_discount_offset(event.control.end_value)
        event.control.start_value = start_offset
        event.control.end_value = end_offset
        start_value = self.__from_discount_offset(start_offset)
        end_value = self.__from_discount_offset(end_offset)
        self.__discount_from_value = None if start_offset <= 0 else start_value
        self.__discount_to_value = None if end_offset >= self.__discount_slider_max_offset else end_value
        self.__sync_discount_filter_keys()
        self.__update_discount_range_text()
        self.safe_update(self.__discount_range_text)

    def __update_discount_range_text(self) -> None:
        from_value = self.__discount_from_value if self.__discount_from_value is not None else self.__discount_steps[0]
        to_value = self.__discount_to_value if self.__discount_to_value is not None else self.__discount_steps[-1]
        self.__discount_range_text.value = (
            f"{self._translation.get('discount_from')}: {(from_value * 100):.0f}%\n"
            f"{self._translation.get('discount_to')}: {(to_value * 100):.0f}%"
        )

    def __sync_discount_filter_keys(self) -> None:
        self.__discount_from_filter_key = (
            self.__to_discount_key(self.__discount_from_value) if self.__discount_from_value is not None else None
        )
        self.__discount_to_filter_key = (
            self.__to_discount_key(self.__discount_to_value) if self.__discount_to_value is not None else None
        )

    def __normalize_initial_discount_range(
        self,
        discount_from_key: str,
        discount_to_key: str,
    ) -> tuple[float | None, float | None]:
        parsed_from = self.__parse_discount_key(discount_from_key)
        parsed_to = self.__parse_discount_key(discount_to_key)
        start_offset = self.__to_discount_offset(parsed_from) if parsed_from is not None else 0
        end_offset = (
            self.__to_discount_offset(parsed_to) if parsed_to is not None else self.__discount_slider_max_offset
        )
        if start_offset > end_offset:
            start_offset = end_offset
        normalized_from = None if start_offset <= 0 else self.__from_discount_offset(start_offset)
        normalized_to = (
            None if end_offset >= self.__discount_slider_max_offset else self.__from_discount_offset(end_offset)
        )
        return normalized_from, normalized_to

    def __to_discount_offset(self, value: float) -> int:
        closest_index = min(
            range(len(self.__discount_steps)),
            key=lambda index: abs(self.__discount_steps[index] - value),
        )
        return max(0, min(closest_index, self.__discount_slider_max_offset))

    def __from_discount_offset(self, offset: int) -> float:
        index = max(0, min(offset, self.__discount_slider_max_offset))
        return self.__discount_steps[index]

    def __coerce_discount_offset(self, raw_offset: int | float) -> int:
        offset = int(round(raw_offset))
        return max(0, min(offset, self.__discount_slider_max_offset))

    @staticmethod
    def __parse_discount_key(value: str) -> float | None:
        stripped = value.strip()
        if stripped in {"", "0"}:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None

    @staticmethod
    def __resolve_discount_steps(discount_options: list[tuple[str, str]]) -> list[float]:
        parsed_steps: list[float] = []
        for key, _ in discount_options:
            try:
                parsed_steps.append(float(key))
            except ValueError:
                continue
        unique_steps = sorted(set(parsed_steps))
        if not unique_steps:
            unique_steps = [0.0, 1.0]
        if len(unique_steps) == 1:
            unique_steps = [unique_steps[0], unique_steps[0]]
        return unique_steps

    @staticmethod
    def __to_discount_key(value: float) -> str:
        return f"{value:.2f}"
