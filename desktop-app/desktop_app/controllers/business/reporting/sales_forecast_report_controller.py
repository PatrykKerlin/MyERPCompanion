from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import date
from io import BytesIO

import flet as ft
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.category_schema import CategoryPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from schemas.business.reporting.sales_forecast_report_schema import (
    SalesForecastReportFilterSchema,
    SalesForecastReportResponseSchema,
    SalesForecastReportRowSchema,
    SalesForecastReportTotalsSchema,
)
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema
from services.business.logistic import CategoryService, ItemService
from services.business.reporting import SalesForecastReportService
from services.business.trade import CurrencyService, CustomerService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.reporting.sales_forecast_report_view import SalesForecastReportView


class SalesForecastReportController(
    BaseViewController[
        SalesForecastReportService,
        SalesForecastReportView,
        SalesForecastReportRowSchema,
        SalesForecastReportFilterSchema,
    ]
):
    plt.switch_backend("Agg")
    __view_chart_size = (8.0, 4.5)
    __view_chart_dpi = 100
    __dialog_chart_size = (12.0, 6.75)
    __dialog_chart_dpi = 200

    _plain_schema_cls = SalesForecastReportRowSchema
    _strict_schema_cls = SalesForecastReportFilterSchema
    _service_cls = SalesForecastReportService
    _view_cls = SalesForecastReportView
    _endpoint = Endpoint.SALES_FORECAST_REPORT
    _view_key = View.SALES_FORECAST_REPORT

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
        self.__discount_from: float | None = None
        self.__discount_to: float | None = None

    def on_apply_filters_clicked(
        self,
        date_from: date | None,
        date_to: date | None,
        currency_id: str | None,
        customer_id: str | None,
        item_id: str | None,
        category_id: str | None,
        discount_from: str | None,
        discount_to: str | None,
    ) -> None:
        self._page.run_task(
            self.__handle_apply_filters,
            date_from,
            date_to,
            currency_id,
            customer_id,
            item_id,
            category_id,
            discount_from,
            discount_to,
        )

    def on_clear_filters_clicked(self) -> None:
        self._page.run_task(self.__handle_clear_filters)

    async def _build_view(
        self,
        translation: Translation,
        mode: ViewMode,
        event: ViewRequested,
    ) -> SalesForecastReportView:
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
        totals = self.__to_totals(response.totals)
        net_monthly_chart = self.__build_monthly_net_chart(response.items, for_dialog=False)
        gross_monthly_chart = self.__build_monthly_gross_chart(response.items, for_dialog=False)
        net_monthly_chart_dialog = self.__build_monthly_net_chart(response.items, for_dialog=True)
        gross_monthly_chart_dialog = self.__build_monthly_gross_chart(response.items, for_dialog=True)
        return SalesForecastReportView(
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
            discount_options=self.__to_discount_options(response.totals.discount_steps),
            currency_id=self.__currency_id,
            customer_id=self.__customer_id,
            item_id=self.__item_id,
            category_id=self.__category_id,
            discount_from_key=self.__to_discount_key(self.__discount_from),
            discount_to_key=self.__to_discount_key(self.__discount_to),
            net_monthly_chart=net_monthly_chart,
            gross_monthly_chart=gross_monthly_chart,
            net_monthly_chart_dialog=net_monthly_chart_dialog,
            gross_monthly_chart_dialog=gross_monthly_chart_dialog,
        )

    async def __handle_apply_filters(
        self,
        date_from: date | None,
        date_to: date | None,
        currency_id: str | None,
        customer_id: str | None,
        item_id: str | None,
        category_id: str | None,
        discount_from: str | None,
        discount_to: str | None,
    ) -> None:
        if date_from and date_to and date_from > date_to:
            self._open_error_dialog(message=self.__t("date_range_invalid"))
            return
        try:
            parsed_currency_id = self.__parse_optional_positive_int(currency_id, "currency")
            parsed_customer_id = self.__parse_optional_positive_int(customer_id, "customer")
            parsed_item_id = self.__parse_optional_positive_int(item_id, "item")
            parsed_category_id = self.__parse_optional_positive_int(category_id, "category")
            parsed_discount_from = self.__parse_optional_discount(discount_from)
            parsed_discount_to = self.__parse_optional_discount(discount_to)
        except ValueError as error:
            self._open_error_dialog(message=str(error))
            return
        if parsed_discount_from is not None and parsed_discount_to is not None and parsed_discount_from > parsed_discount_to:
            self._open_error_dialog(message=self.__t("discount_range_invalid"))
            return
        self.__date_from = date_from
        self.__date_to = date_to
        self.__currency_id = parsed_currency_id
        self.__customer_id = parsed_customer_id
        self.__item_id = parsed_item_id
        self.__category_id = parsed_category_id
        self.__discount_from = parsed_discount_from
        self.__discount_to = parsed_discount_to
        await self.__refresh_view()

    async def __handle_clear_filters(self) -> None:
        self.__date_from = None
        self.__date_to = None
        self.__currency_id = None
        self.__customer_id = None
        self.__item_id = None
        self.__category_id = None
        self.__discount_from = None
        self.__discount_to = None
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
        net_monthly_chart = self.__build_monthly_net_chart(response.items, for_dialog=False)
        gross_monthly_chart = self.__build_monthly_gross_chart(response.items, for_dialog=False)
        net_monthly_chart_dialog = self.__build_monthly_net_chart(response.items, for_dialog=True)
        gross_monthly_chart_dialog = self.__build_monthly_gross_chart(response.items, for_dialog=True)
        self._view.set_report_data(
            totals=totals,
            net_monthly_chart=net_monthly_chart,
            gross_monthly_chart=gross_monthly_chart,
            net_monthly_chart_dialog=net_monthly_chart_dialog,
            gross_monthly_chart_dialog=gross_monthly_chart_dialog,
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
    async def __perform_get_report(self) -> SalesForecastReportResponseSchema:
        params: dict[str, str | int | float] = {}
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
        if self.__discount_from is not None:
            params["discount_from"] = self.__discount_from
        if self.__discount_to is not None:
            params["discount_to"] = self.__discount_to
        return await self._service.get_report(Endpoint.SALES_FORECAST_REPORT, None, params, None, self._module_id)

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

    def __parse_optional_discount(self, value: str | None) -> float | None:
        if value is None:
            return None
        stripped = value.strip().replace(",", ".")
        if stripped in {"", "0"}:
            return None
        try:
            parsed_value = float(stripped)
        except ValueError as error:
            raise ValueError(self.__t("discount_percent_invalid")) from error
        if parsed_value < 0:
            raise ValueError(self.__t("discount_percent_invalid"))
        if parsed_value > 100:
            raise ValueError(self.__t("discount_percent_invalid"))
        if parsed_value > 1:
            return parsed_value / 100.0
        return parsed_value

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
    def __to_totals(totals: SalesForecastReportTotalsSchema) -> dict[str, str]:
        return {
            "rows_count": str(totals.rows_count),
            "periods_count": str(totals.periods_count),
            "total_predicted_net": f"{totals.total_predicted_net:.2f}",
            "total_predicted_gross": f"{totals.total_predicted_gross:.2f}",
        }

    @staticmethod
    def __to_discount_options(discount_steps: list[float]) -> list[tuple[str, str]]:
        unique_steps = sorted(set(float(step) for step in discount_steps))
        return [(SalesForecastReportController.__to_discount_key(step), f"{step * 100:.0f}%") for step in unique_steps]

    @staticmethod
    def __to_discount_key(discount: float | None) -> str:
        if discount is None:
            return "0"
        return f"{discount:.4f}"

    def __build_monthly_net_chart(self, rows: list[SalesForecastReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        monthly_sums: dict[date, float] = defaultdict(float)
        for row in rows:
            monthly_sums[row.predicted_at] += row.predicted_net
        if not monthly_sums:
            return None
        sorted_dates = sorted(monthly_sums.keys())
        values = [monthly_sums[item] for item in sorted_dates]
        return self.__build_line_chart(
            date_values=sorted_dates,
            values=values,
            title=self.__t("predicted_net_by_month"),
            for_dialog=for_dialog,
        )

    def __build_monthly_gross_chart(self, rows: list[SalesForecastReportRowSchema], for_dialog: bool) -> bytes | None:
        if not rows:
            return None
        monthly_sums: dict[date, float] = defaultdict(float)
        for row in rows:
            monthly_sums[row.predicted_at] += row.predicted_gross
        if not monthly_sums:
            return None
        sorted_dates = sorted(monthly_sums.keys())
        values = [monthly_sums[item] for item in sorted_dates]
        return self.__build_line_chart(
            date_values=sorted_dates,
            values=values,
            title=self.__t("predicted_gross_by_month"),
            for_dialog=for_dialog,
        )

    def __build_line_chart(
        self,
        date_values: list[date],
        values: list[float],
        title: str,
        for_dialog: bool,
    ) -> bytes | None:
        theme_style = self.__get_chart_theme()
        chart_size, chart_dpi = self.__get_chart_render_settings(for_dialog)
        figure = None
        try:
            sns.set_theme(style=theme_style)
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
            axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.2f}"))
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
            return SalesForecastReportController.__dialog_chart_size, SalesForecastReportController.__dialog_chart_dpi
        return SalesForecastReportController.__view_chart_size, SalesForecastReportController.__view_chart_dpi

    def __get_chart_theme(self) -> str:
        if self.__is_dark_theme():
            return "darkgrid"
        return "whitegrid"

    def __is_dark_theme(self) -> bool:
        user = self._state_store.app_state.user.current
        selected_theme = user.theme if user else self._settings.THEME
        if selected_theme == "dark":
            return True
        if selected_theme == "light":
            return False
        return self._page.platform_brightness == ft.Brightness.DARK
