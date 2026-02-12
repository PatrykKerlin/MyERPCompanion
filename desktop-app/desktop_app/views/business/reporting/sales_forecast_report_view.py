from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, cast

import flet as ft
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_desktop_view import BaseDesktopView
from views.controls.date_field_control import DateField

if TYPE_CHECKING:
    from controllers.business.reporting.sales_forecast_report_controller import SalesForecastReportController


class SalesForecastReportView(BaseDesktopView):
    def __init__(
        self,
        controller: SalesForecastReportController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        totals: dict[str, str],
        date_from: date | None,
        date_to: date | None,
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
        gross_monthly_chart: bytes | None,
        net_monthly_chart_dialog: bytes | None,
        gross_monthly_chart_dialog: bytes | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None

        self.__totals = dict(totals)
        self.__net_monthly_chart = net_monthly_chart
        self.__gross_monthly_chart = gross_monthly_chart
        self.__net_monthly_chart_dialog = net_monthly_chart_dialog
        self.__gross_monthly_chart_dialog = gross_monthly_chart_dialog

        date_from_container, _ = self._get_date_picker("date_from", 2, value=date_from, read_only=False)
        self.__date_from_input = cast(DateField, date_from_container.content)

        date_to_container, _ = self._get_date_picker("date_to", 2, value=date_to, read_only=False)
        self.__date_to_input = cast(DateField, date_to_container.content)

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

        discount_from_container, _ = self._get_dropdown("discount_from", 2, discount_options)
        self.__discount_from_input = cast(ft.Dropdown, discount_from_container.content)
        self.__discount_from_input.label = self._translation.get("discount_from")
        self.__discount_from_input.value = discount_from_key

        discount_to_container, _ = self._get_dropdown("discount_to", 2, discount_options)
        self.__discount_to_input = cast(ft.Dropdown, discount_to_container.content)
        self.__discount_to_input.label = self._translation.get("discount_to")
        self.__discount_to_input.value = discount_to_key

        self._inputs.update(
            {
                "date_from": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(date_from_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "date_to": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(date_to_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "currency_id": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(currency_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "customer_id": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(customer_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "item_id": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(item_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "category_id": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(category_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "discount_from": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(discount_from_container, 0),
                    marker=(ft.Container(), 0),
                ),
                "discount_to": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(discount_to_container, 0),
                    marker=(ft.Container(), 0),
                ),
            }
        )

        self.__totals_row = ft.ResponsiveRow(
            columns=15,
            spacing=8,
            run_spacing=8,
            controls=[],
        )
        self.__monthly_chart_container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
        self.__discount_chart_container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

        self.__build_layout()
        self.__render_report()

    def set_report_data(
        self,
        totals: dict[str, str],
        net_monthly_chart: bytes | None,
        gross_monthly_chart: bytes | None,
        net_monthly_chart_dialog: bytes | None,
        gross_monthly_chart_dialog: bytes | None,
    ) -> None:
        self.__totals = dict(totals)
        self.__net_monthly_chart = net_monthly_chart
        self.__gross_monthly_chart = gross_monthly_chart
        self.__net_monthly_chart_dialog = net_monthly_chart_dialog
        self.__gross_monthly_chart_dialog = gross_monthly_chart_dialog
        self.__render_report()

    def reset_filters(self) -> None:
        self.__date_from_input.value = None
        self.__date_to_input.value = None
        self.__currency_input.value = "0"
        self.__customer_input.value = "0"
        self.__item_input.value = "0"
        self.__category_input.value = "0"
        self.__discount_from_input.value = "0"
        self.__discount_to_input.value = "0"
        self.__safe_update(self.__currency_input)
        self.__safe_update(self.__customer_input)
        self.__safe_update(self.__item_input)
        self.__safe_update(self.__category_input)
        self.__safe_update(self.__discount_from_input)
        self.__safe_update(self.__discount_to_input)

    def __build_layout(self) -> None:
        apply_button = ft.Button(
            content=self._translation.get("apply_filters"),
            on_click=lambda _: self._controller.on_apply_filters_clicked(
                date_from=self.__date_from_input.value,
                date_to=self.__date_to_input.value,
                currency_id=self.__currency_input.value,
                customer_id=self.__customer_input.value,
                item_id=self.__item_input.value,
                category_id=self.__category_input.value,
                discount_from=self.__discount_from_input.value,
                discount_to=self.__discount_to_input.value,
            ),
        )
        clear_button = ft.TextButton(
            self._translation.get("clear_filters"),
            on_click=lambda _: self._controller.on_clear_filters_clicked(),
        )

        filters = ft.ResponsiveRow(
            columns=12,
            controls=[
                self.__build_filter_input(self._translation.get("date_from"), self.__date_from_input),
                self.__build_filter_input(self._translation.get("date_to"), self.__date_to_input),
                self.__build_filter_input(self._translation.get("currency"), self.__currency_input),
                self.__build_filter_input(self._translation.get("customer"), self.__customer_input),
                self.__build_filter_input(self._translation.get("item"), self.__item_input),
                self.__build_filter_input(self._translation.get("category"), self.__category_input),
                ft.Container(col={"sm": 12, "md": 2}, content=self.__discount_from_input),
                ft.Container(col={"sm": 12, "md": 2}, content=self.__discount_to_input),
                ft.Container(
                    col={"sm": 12},
                    content=ft.Row(
                        controls=[apply_button, clear_button],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ),
            ],
        )

        charts = ft.Row(
            expand=True,
            spacing=12,
            controls=[
                ft.Container(expand=1, content=self.__monthly_chart_container),
                ft.Container(expand=1, content=self.__discount_chart_container),
            ],
        )

        self._master_column.controls = [
            filters,
            self.__totals_row,
            charts,
        ]
        self.content = ft.Container(content=self._master_column, expand=True)

    def __build_filter_input(self, label: str, control: ft.Control) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 2},
            content=ft.Column(
                controls=[ft.Text(label), control],
            ),
        )

    def __render_report(self) -> None:
        self.__render_totals()
        self.__render_charts()

    def __render_totals(self) -> None:
        self.__totals_row.controls = [
            self.__build_total_item("rows_count", self.__totals.get("rows_count", "0")),
            self.__build_total_item("periods_count", self.__totals.get("periods_count", "0")),
            self.__build_total_item("total_predicted_net", self.__totals.get("total_predicted_net", "0.00")),
            self.__build_total_item("total_predicted_gross", self.__totals.get("total_predicted_gross", "0.00")),
        ]
        self.__safe_update(self.__totals_row)

    def __build_total_item(self, label_key: str, value: str) -> ft.Container:
        return ft.Container(
            col={"sm": 15, "md": 3},
            content=ft.Column(
                controls=[
                    ft.Text(self._translation.get(label_key)),
                    ft.Text(value),
                ],
            ),
        )

    def __render_charts(self) -> None:
        self.__monthly_chart_container.content = self.__build_chart_content(
            self._translation.get("predicted_net_by_month"),
            self.__net_monthly_chart,
            self.__net_monthly_chart_dialog,
        )
        self.__discount_chart_container.content = self.__build_chart_content(
            self._translation.get("predicted_gross_by_month"),
            self.__gross_monthly_chart,
            self.__gross_monthly_chart_dialog,
        )
        self.__safe_update(self.__monthly_chart_container)
        self.__safe_update(self.__discount_chart_container)

    def __build_chart_content(self, title: str, chart: bytes | None, dialog_chart: bytes | None) -> ft.Control:
        if not chart:
            image_holder: ft.Control = ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(self._translation.get("no_chart_data")),
            )
        else:
            image_holder = ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                on_click=lambda _, image=(dialog_chart or chart), chart_title=title: self.__open_chart_dialog(
                    image,
                    chart_title,
                ),
                content=ft.Image(src=chart, fit=ft.BoxFit.CONTAIN, expand=True),
            )
        return ft.Column(
            expand=True,
            controls=[
                ft.Text(title),
                image_holder,
            ],
        )

    def __open_chart_dialog(self, chart: bytes, title: str) -> None:
        content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Image(
                src=chart,
                fit=ft.BoxFit.CONTAIN,
                expand=True,
            ),
        )
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=content,
            actions=[
                ft.TextButton(
                    self._translation.get("close"),
                    on_click=lambda _: self.__close_dialog(dialog),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dialog)
        self.__safe_update(self.page)

    def __close_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.close(dialog)
        self.__safe_update(self.page)

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        control.update()
