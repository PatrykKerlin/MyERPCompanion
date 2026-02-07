from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import date
from io import BytesIO

import flet as ft
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.category_schema import CategoryPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from schemas.business.reporting.sales_report_schema import (
    SalesReportFilterSchema,
    SalesReportResponseSchema,
    SalesReportRowSchema,
    SalesReportTotalsSchema,
)
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema
from services.business.logistic import CategoryService, ItemService
from services.business.reporting import SalesReportService
from services.business.trade import CurrencyService, CustomerService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.reporting.sales_report_view import SalesReportView


class SalesReportController(
    BaseViewController[SalesReportService, SalesReportView, SalesReportRowSchema, SalesReportFilterSchema]
):
    plt.switch_backend("Agg")
    __view_chart_size = (8.0, 4.5)
    __view_chart_dpi = 100
    __dialog_chart_size = (12.0, 6.75)
    __dialog_chart_dpi = 200

    _plain_schema_cls = SalesReportRowSchema
    _strict_schema_cls = SalesReportFilterSchema
    _service_cls = SalesReportService
    _view_cls = SalesReportView
    _endpoint = Endpoint.SALES_REPORT
    _view_key = View.SALES_REPORT

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__category_service = CategoryService(self._settings, self._logger, self._tokens_accessor)

        self.__date_from: date | None = None
        self.__date_to: date | None = None
        self.__currency_id: int | None = None
        self.__customer_id: int | None = None
        self.__item_id: int | None = None
        self.__category_id: int | None = None

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> SalesReportView:
        mode = ViewMode.STATIC
        currencies, customers, items, categories, response = await asyncio.gather(
            self.__perform_get_currencies(),
            self.__perform_get_customers(),
            self.__perform_get_items(),
            self.__perform_get_categories(),
            self.__perform_get_report(),
        )
        currency_options = self.__to_currency_options(currencies or [])
        customer_options = self.__to_customer_options(customers or [])
        item_options = self.__to_item_options(items or [])
        category_options = self.__to_category_options(categories or [])
        totals = self.__to_totals(response.totals, show_amounts=self.__currency_id is not None)
        category_chart = self.__build_category_chart(response.items, for_dialog=False)
        daily_chart = self.__build_daily_chart(response.items, for_dialog=False)
        category_chart_dialog = self.__build_category_chart(response.items, for_dialog=True)
        daily_chart_dialog = self.__build_daily_chart(response.items, for_dialog=True)
        return SalesReportView(
            controller=self,
            translation=translation,
            mode=mode,
            key=event.view_key,
            totals=totals,
            date_from=self.__date_from,
            date_to=self.__date_to,
            currency_options=currency_options,
            customer_options=customer_options,
            item_options=item_options,
            category_options=category_options,
            currency_id=self.__currency_id,
            customer_id=self.__customer_id,
            item_id=self.__item_id,
            category_id=self.__category_id,
            category_chart=category_chart,
            daily_chart=daily_chart,
            category_chart_dialog=category_chart_dialog,
            daily_chart_dialog=daily_chart_dialog,
        )

    def on_apply_filters_clicked(
        self,
        date_from: date | None,
        date_to: date | None,
        currency_id: str | None,
        customer_id: str | None,
        item_id: str | None,
        category_id: str | None,
    ) -> None:
        self._page.run_task(
            self.__handle_apply_filters,
            date_from,
            date_to,
            currency_id,
            customer_id,
            item_id,
            category_id,
        )

    def on_clear_filters_clicked(self) -> None:
        self._page.run_task(self.__handle_clear_filters)

    async def __handle_apply_filters(
        self,
        date_from: date | None,
        date_to: date | None,
        currency_id: str | None,
        customer_id: str | None,
        item_id: str | None,
        category_id: str | None,
    ) -> None:
        if date_from and date_to and date_from > date_to:
            self._open_error_dialog(message=self.__t("date_range_invalid"))
            return
        try:
            parsed_currency_id = self.__parse_optional_positive_int(currency_id, "currency")
            parsed_customer_id = self.__parse_optional_positive_int(customer_id, "customer")
            parsed_item_id = self.__parse_optional_positive_int(item_id, "item")
            parsed_category_id = self.__parse_optional_positive_int(category_id, "category")
        except ValueError as error:
            self._open_error_dialog(message=str(error))
            return
        self.__date_from = date_from
        self.__date_to = date_to
        self.__currency_id = parsed_currency_id
        self.__customer_id = parsed_customer_id
        self.__item_id = parsed_item_id
        self.__category_id = parsed_category_id
        await self.__refresh_view()

    async def __handle_clear_filters(self) -> None:
        self.__date_from = None
        self.__date_to = None
        self.__currency_id = None
        self.__customer_id = None
        self.__item_id = None
        self.__category_id = None
        if self._view:
            self._view.reset_filters()
        await self.__refresh_view()

    async def __refresh_view(self) -> None:
        if not self._view:
            return
        response = await self.__perform_get_report()
        if response is None:
            return
        totals = self.__to_totals(response.totals, show_amounts=self.__currency_id is not None)
        category_chart = self.__build_category_chart(response.items, for_dialog=False)
        daily_chart = self.__build_daily_chart(response.items, for_dialog=False)
        category_chart_dialog = self.__build_category_chart(response.items, for_dialog=True)
        daily_chart_dialog = self.__build_daily_chart(response.items, for_dialog=True)
        self._view.set_report_data(
            totals=totals,
            category_chart=category_chart,
            daily_chart=daily_chart,
            category_chart_dialog=category_chart_dialog,
            daily_chart_dialog=daily_chart_dialog,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_currencies(self) -> list[CurrencyPlainSchema]:
        return await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customers(self) -> list[CustomerPlainSchema]:
        return await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items(self) -> list[ItemPlainSchema]:
        return await self.__item_service.get_all(Endpoint.ITEMS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_categories(self) -> list[CategoryPlainSchema]:
        return await self.__category_service.get_all(Endpoint.CATEGORIES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_report(self) -> SalesReportResponseSchema:
        params: dict[str, str | int] = {}
        if self.__date_from is not None:
            params["date_from"] = self.__date_from.isoformat()
        if self.__date_to is not None:
            params["date_to"] = self.__date_to.isoformat()
        if self.__currency_id is not None:
            params["currency_id"] = self.__currency_id
        if self.__customer_id is not None:
            params["customer_id"] = self.__customer_id
        if self.__item_id is not None:
            params["item_id"] = self.__item_id
        if self.__category_id is not None:
            params["category_id"] = self.__category_id
        return await self._service.get_report(Endpoint.SALES_REPORT, None, params, None, self._module_id)

    def __parse_optional_positive_int(self, value: str | None, label_key: str) -> int | None:
        if value is None:
            return None
        stripped = value.strip()
        if stripped in {"", "0"}:
            return None
        if not stripped.isdigit():
            label = self.__t(label_key)
            raise ValueError(self.__t("must_be_positive_integer").format(label=label))
        parsed_value = int(stripped)
        if parsed_value <= 0:
            label = self.__t(label_key)
            raise ValueError(self.__t("must_be_positive_integer").format(label=label))
        return parsed_value

    def __t(self, key: str) -> str:
        return self._state_store.app_state.translation.items.get(key)

    @staticmethod
    def __to_customer_options(customers: list[CustomerPlainSchema]) -> list[tuple[int, str]]:
        options = [(customer.id, customer.company_name) for customer in customers]
        return sorted(options, key=lambda option: option[1].lower())

    @staticmethod
    def __to_currency_options(currencies: list[CurrencyPlainSchema]) -> list[tuple[int, str]]:
        options = [(currency.id, f"{currency.code} ({currency.name})") for currency in currencies]
        return sorted(options, key=lambda option: option[1].lower())

    @staticmethod
    def __to_item_options(items: list[ItemPlainSchema]) -> list[tuple[int, str]]:
        options = [(item.id, item.name) for item in items]
        return sorted(options, key=lambda option: option[1].lower())

    @staticmethod
    def __to_category_options(categories: list[CategoryPlainSchema]) -> list[tuple[int, str]]:
        options = [(category.id, category.name) for category in categories]
        return sorted(options, key=lambda option: option[1].lower())

    @staticmethod
    def __to_totals(totals: SalesReportTotalsSchema, show_amounts: bool) -> dict[str, str]:
        total_net = f"{totals.total_net:.2f}" if show_amounts else ""
        total_vat = f"{totals.total_vat:.2f}" if show_amounts else ""
        total_gross = f"{totals.total_gross:.2f}" if show_amounts else ""
        total_discount = f"{totals.total_discount:.2f}" if show_amounts else ""
        return {
            "orders_count": str(totals.orders_count),
            "rows_count": str(totals.rows_count),
            "quantity": str(totals.quantity),
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_discount": total_discount,
        }

    def __build_category_chart(self, rows: list[SalesReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        category_sums: dict[str, float] = defaultdict(float)
        for row in rows:
            category_sums[row.category_name] += row.total_gross
        if not category_sums:
            return None
        sorted_data = sorted(category_sums.items(), key=lambda item: item[1], reverse=True)[:8]
        labels = [item[0] for item in sorted_data]
        values = [item[1] for item in sorted_data]
        return self.__build_bar_chart(
            labels=labels,
            values=values,
            title=self.__t("gross_by_category"),
            for_dialog=for_dialog,
        )

    def __build_daily_chart(self, rows: list[SalesReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        date_sums: dict[date, float] = defaultdict(float)
        for row in rows:
            date_sums[row.order_date] += row.total_gross
        if not date_sums:
            return None
        sorted_dates = sorted(date_sums.keys())
        values = [date_sums[item] for item in sorted_dates]
        return self.__build_line_chart(
            date_values=sorted_dates,
            values=values,
            title=self.__t("gross_by_day"),
            for_dialog=for_dialog,
        )

    def __build_bar_chart(self, labels: list[str], values: list[float], title: str, for_dialog: bool) -> bytes | None:
        theme = self.__get_chart_theme()
        chart_size, chart_dpi = self.__get_chart_render_settings(for_dialog)
        figure = None
        try:
            sns.set_theme(style=theme["style"], rc=theme["rc"])
            figure, axis = plt.subplots(figsize=chart_size)
            sns.barplot(x=labels, y=values, ax=axis, color=theme["bar_color"])
            axis.set_title(title, color=theme["text_color"])
            axis.set_xlabel("")
            axis.set_ylabel("")
            axis.tick_params(axis="x", rotation=30)
            axis.tick_params(axis="y", colors=theme["text_color"])
            axis.tick_params(axis="x", colors=theme["text_color"])
            axis.grid(axis="y", alpha=0.35)
            for spine in axis.spines.values():
                spine.set_color(theme["edge_color"])
            figure.tight_layout()
            buffer = BytesIO()
            figure.savefig(buffer, format="png", dpi=chart_dpi)
            return buffer.getvalue()
        finally:
            if figure is not None:
                plt.close(figure)

    def __build_line_chart(
        self,
        date_values: list[date],
        values: list[float],
        title: str,
        for_dialog: bool,
    ) -> bytes | None:
        theme = self.__get_chart_theme()
        chart_size, chart_dpi = self.__get_chart_render_settings(for_dialog)
        figure = None
        try:
            sns.set_theme(style=theme["style"], rc=theme["rc"])
            figure, axis = plt.subplots(figsize=chart_size)
            sns.lineplot(
                x=date_values,
                y=values,
                ax=axis,
                marker="o",
                linewidth=2.0,
                color=theme["line_color"],
            )
            axis.set_title(title, color=theme["text_color"])
            axis.set_xlabel("")
            axis.set_ylabel("")
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            axis.tick_params(axis="x", rotation=30)
            axis.tick_params(axis="y", colors=theme["text_color"])
            axis.tick_params(axis="x", colors=theme["text_color"])
            axis.grid(axis="y", alpha=0.35)
            for spine in axis.spines.values():
                spine.set_color(theme["edge_color"])
            figure.tight_layout()
            buffer = BytesIO()
            figure.savefig(buffer, format="png", dpi=chart_dpi)
            return buffer.getvalue()
        finally:
            if figure is not None:
                plt.close(figure)

    @staticmethod
    def __get_chart_render_settings(for_dialog: bool) -> tuple[tuple[float, float], int]:
        if for_dialog:
            return SalesReportController.__dialog_chart_size, SalesReportController.__dialog_chart_dpi
        return SalesReportController.__view_chart_size, SalesReportController.__view_chart_dpi

    def __get_chart_theme(self) -> dict[str, str | dict[str, str]]:
        if self.__is_dark_theme():
            return {
                "style": "darkgrid",
                "bar_color": "#66BB6A",
                "line_color": "#64B5F6",
                "text_color": "#ECEFF1",
                "edge_color": "#90A4AE",
                "rc": {
                    "figure.facecolor": "#1E1E1E",
                    "axes.facecolor": "#262626",
                    "axes.edgecolor": "#90A4AE",
                    "axes.labelcolor": "#ECEFF1",
                    "xtick.color": "#ECEFF1",
                    "ytick.color": "#ECEFF1",
                    "grid.color": "#5F6368",
                    "text.color": "#ECEFF1",
                },
            }
        return {
            "style": "whitegrid",
            "bar_color": "#2E7D32",
            "line_color": "#1565C0",
            "text_color": "#263238",
            "edge_color": "#90A4AE",
            "rc": {
                "figure.facecolor": "#FFFFFF",
                "axes.facecolor": "#FFFFFF",
                "axes.edgecolor": "#90A4AE",
                "axes.labelcolor": "#263238",
                "xtick.color": "#263238",
                "ytick.color": "#263238",
                "grid.color": "#CFD8DC",
                "text.color": "#263238",
            },
        }

    def __is_dark_theme(self) -> bool:
        user = self._state_store.app_state.user.current
        selected_theme = user.theme if user else self._settings.THEME
        if selected_theme == "dark":
            return True
        if selected_theme == "light":
            return False
        return self._page.platform_brightness == ft.Brightness.DARK
