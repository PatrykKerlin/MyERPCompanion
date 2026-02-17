from __future__ import annotations

import asyncio
import math
from collections import defaultdict
from datetime import date
from io import BytesIO

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from matplotlib.ticker import FuncFormatter
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

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> SalesReportView:
        view_mode = ViewMode.STATIC
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
        totals = self.__to_totals(response.totals)
        category_chart = self.__build_category_chart(response.items, for_dialog=False)
        daily_chart = self.__build_daily_chart(response.items, for_dialog=False)
        category_chart_dialog = self.__build_category_chart(response.items, for_dialog=True)
        daily_chart_dialog = self.__build_daily_chart(response.items, for_dialog=True)
        return SalesReportView(
            controller=self,
            translation=translation,
            mode=view_mode,
            key=event.view_key,
            totals=totals,
            date_from=self.__date_from,
            date_to=self.__date_to,
            first_sales_date=response.first_sales_date,
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

    async def __handle_apply_filters(
        self,
        date_from: date | None,
        date_to: date | None,
        currency_id: str | None,
        customer_id: str | None,
        item_id: str | None,
        category_id: str | None,
    ) -> None:
        translation = self._state_store.app_state.translation.items
        if date_from and date_to and date_from > date_to:
            self._open_error_dialog(message=translation.get("date_range_invalid"))
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
        totals = self.__to_totals(response.totals)
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
        translation = self._state_store.app_state.translation.items
        if value is None:
            return None
        stripped = value.strip()
        if stripped in {"", "0"}:
            return None
        if not stripped.isdigit():
            label = translation.get(label_key)
            raise ValueError(translation.get("must_be_positive_integer").format(label=label))
        parsed_value = int(stripped)
        if parsed_value <= 0:
            label = translation.get(label_key)
            raise ValueError(translation.get("must_be_positive_integer").format(label=label))
        return parsed_value

    @staticmethod
    def __to_customer_options(customers: list[CustomerPlainSchema]) -> list[tuple[int, str]]:
        options = [(customer.id, customer.company_name) for customer in customers]
        return sorted(options, key=lambda option: option[1].lower())

    @staticmethod
    def __to_currency_options(currencies: list[CurrencyPlainSchema]) -> list[tuple[int, str]]:
        options = [(currency.id, f"{currency.code} {currency.name}") for currency in currencies]
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
    def __to_totals(totals: SalesReportTotalsSchema) -> dict[str, str]:
        return {
            "orders_count": SalesReportController.__format_grouped_int(totals.orders_count),
            "rows_count": SalesReportController.__format_grouped_int(totals.rows_count),
            "quantity": SalesReportController.__format_grouped_int(totals.quantity),
            "total_net": SalesReportController.__format_grouped_int(math.trunc(totals.total_net)),
            "total_vat": SalesReportController.__format_grouped_int(math.trunc(totals.total_vat)),
            "total_gross": SalesReportController.__format_grouped_int(math.trunc(totals.total_gross)),
            "total_discount": SalesReportController.__format_grouped_int(math.trunc(totals.total_discount)),
        }

    @staticmethod
    def __format_grouped_int(value: int) -> str:
        return f"{value:,}".replace(",", " ")

    def __build_category_chart(self, rows: list[SalesReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        translation = self._state_store.app_state.translation.items
        category_sums: dict[str, float] = defaultdict(float)
        for row in rows:
            category_sums[row.category_name] += row.total_net
        if not category_sums:
            return None
        sorted_data = sorted(category_sums.items(), key=lambda item: item[1], reverse=True)[:8]
        labels = [item[0] for item in sorted_data]
        values = [item[1] for item in sorted_data]
        return self.__build_bar_chart(
            labels=labels,
            values=values,
            title=translation.get("total_net"),
            for_dialog=for_dialog,
        )

    def __build_daily_chart(self, rows: list[SalesReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        translation = self._state_store.app_state.translation.items
        date_sums: dict[date, int] = defaultdict(int)
        for row in rows:
            date_sums[row.order_date] += row.quantity
        if not date_sums:
            return None
        sorted_dates = sorted(date_sums.keys())
        values = [float(date_sums[item]) for item in sorted_dates]
        return self.__build_line_chart(
            date_values=sorted_dates,
            values=values,
            title=translation.get("total_quantity"),
            for_dialog=for_dialog,
        )

    def __build_bar_chart(self, labels: list[str], values: list[float], title: str, for_dialog: bool) -> bytes | None:
        chart_size, chart_dpi = self.__get_chart_render_settings(for_dialog)
        figure = None
        try:
            sns.set_theme(style="darkgrid")
            figure, axis = plt.subplots(figsize=chart_size)
            sns.barplot(x=labels, y=values, ax=axis)
            axis.set_title(title)
            axis.set_xlabel("")
            axis.set_ylabel("")
            axis.tick_params(axis="x", rotation=30)
            axis.ticklabel_format(axis="y", style="plain", useOffset=False)
            axis.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: SalesReportController.__format_grouped_int(math.trunc(value)))
            )
            axis.grid(axis="y", alpha=0.35)
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
        chart_size, chart_dpi = self.__get_chart_render_settings(for_dialog)
        figure = None
        try:
            sns.set_theme(style="darkgrid")
            figure, axis = plt.subplots(figsize=chart_size)
            sns.lineplot(
                x=date_values,
                y=values,
                ax=axis,
                marker="o",
                linewidth=2.0,
            )
            axis.set_title(title)
            axis.set_xlabel("")
            axis.set_ylabel("")
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            axis.ticklabel_format(axis="y", style="plain", useOffset=False)
            axis.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: SalesReportController.__format_grouped_int(math.trunc(value)))
            )
            axis.tick_params(axis="x", rotation=30)
            axis.grid(axis="y", alpha=0.35)
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
