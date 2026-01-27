from datetime import date, timedelta
from typing import Callable

import flet as ft

from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, OrderInvoiceBulkStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from services.business.trade import (
    AssocOrderStatusService,
    CurrencyService,
    CustomerService,
    InvoiceService,
    OrderService,
    StatusService,
)
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.invoice_view import InvoiceView
from events.events import ViewRequested
from config.context import Context


class InvoiceController(BaseViewController[InvoiceService, InvoiceView, InvoicePlainSchema, InvoiceStrictSchema]):
    _plain_schema_cls = InvoicePlainSchema
    _strict_schema_cls = InvoiceStrictSchema
    _service_cls = InvoiceService
    _view_cls = InvoiceView
    _endpoint = Endpoint.INVOICES
    _view_key = View.INVOICES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_payment_terms: dict[int, int] = {}
        self.__prefetched_create_number: str | None = None
        self.__eligible_status_ids: set[int] = set()
        self.__orders_by_id: dict[int, OrderPlainSchema] = {}
        self.__selected_order_ids: set[int] = set()
        self.__target_rows: list[tuple[int, list[object]]] = []

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> InvoiceView:
        currencies = await self.__perform_get_all_currencies()
        customers = await self.__perform_get_all_customers()
        statuses = await self.__perform_get_all_statuses()
        self.__eligible_status_ids = {status.id for status in statuses if status.order == 4}
        if mode == ViewMode.CREATE:
            self.__prefetched_create_number = await self.__generate_invoice_number(date.today())
        else:
            self.__prefetched_create_number = None
        view = InvoiceView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            currencies,
            customers,
            self.on_orders_save_clicked,
            self.on_orders_delete_clicked,
        )
        self.__reset_orders(view)
        return view

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_customers(self) -> list[tuple[int, str]]:
        schemas = await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)
        self.__customer_payment_terms = {schema.id: schema.payment_term for schema in schemas}
        return [(schema.id, schema.company_name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_orders(self, customer_id: int, currency_id: int) -> list[OrderPlainSchema]:
        response = await self.__order_service.get_page(
            Endpoint.SALES_ORDERS,
            None,
            {"page": 1, "page_size": 200, "customer_id": customer_id, "currency_id": currency_id},
            None,
            self._module_id,
        )
        return response.items

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_statuses(self, order_id: int) -> list[AssocOrderStatusPlainSchema]:
        return await self.__order_status_service.get_all(
            Endpoint.ORDER_STATUSES, None, {"order_id": order_id}, None, self._module_id
        )

    def on_value_changed(self, event: ft.ControlEvent, key: str, *after_change: Callable[[], None]) -> None:
        super().on_value_changed(event, key, *after_change)
        if self._view and self._view.mode == ViewMode.CREATE:
            if key == "customer_id":
                self.__update_due_date_for_customer()
            if key in {"customer_id", "currency_id"}:
                self._page.run_task(self.__reload_orders_for_selection)

    def on_orders_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_orders_save)

    def on_orders_delete_clicked(self, order_ids: list[int]) -> None:
        if not self._view or not order_ids:
            return
        for order_id in order_ids:
            self.__selected_order_ids.discard(order_id)
        self.__target_rows = self.__build_target_rows()
        self._view.set_target_rows(self.__target_rows)
        self._view.mark_source_orders_as_moved(list(self.__selected_order_ids))
        self.__apply_totals_from_selection()

    def get_create_defaults(self) -> dict[str, object]:
        return self.__build_create_defaults()

    def __build_create_defaults(self) -> dict[str, object]:
        today = date.today()
        number = self.__prefetched_create_number or self.__format_invoice_number(today, 1)
        defaults: dict[str, object] = {
            "number": number,
            "issue_date": today,
            "due_date": today,
        }
        return defaults

    def __update_due_date_for_customer(self) -> None:
        if not self._view:
            return
        customer_id = self.__get_selected_customer_id()
        if customer_id is None:
            return
        payment_term = self.__customer_payment_terms.get(customer_id)
        if payment_term is None:
            return
        issue_date = self._request_data.input_values.get("issue_date")
        if isinstance(issue_date, str):
            try:
                issue_date = date.fromisoformat(issue_date)
            except ValueError:
                issue_date = None
        if not isinstance(issue_date, date):
            issue_date = date.today()
        due_date = issue_date + timedelta(days=payment_term)
        self._view.set_due_date(due_date)

    def __get_selected_customer_id(self) -> int | None:
        value = self._request_data.input_values.get("customer_id")
        if isinstance(value, int):
            return value
        if not isinstance(value, str):
            return None
        value = value.strip()
        if value in {"", "0"}:
            return None
        return int(value) if value.isdigit() else None

    def __get_selected_currency_id(self) -> int | None:
        value = self._request_data.input_values.get("currency_id")
        if isinstance(value, int):
            return value
        if not isinstance(value, str):
            return None
        value = value.strip()
        if value in {"", "0"}:
            return None
        return int(value) if value.isdigit() else None

    async def __reload_orders_for_selection(self) -> None:
        if not self._view:
            return
        customer_id = self.__get_selected_customer_id()
        currency_id = self.__get_selected_currency_id()
        if customer_id is None or currency_id is None:
            self.__reset_orders(self._view)
            return
        orders = await self.__load_eligible_orders(customer_id, currency_id)
        self.__orders_by_id = {order.id: order for order in orders}
        self.__selected_order_ids = {order_id for order_id in self.__selected_order_ids if order_id in self.__orders_by_id}
        source_rows = self.__build_source_rows(orders)
        self._view.set_source_rows(source_rows)
        self._view.set_source_enabled(bool(source_rows))
        self._view.set_target_enabled(bool(source_rows))
        self._view.set_target_rows(self.__build_target_rows())
        self._view.mark_source_orders_as_moved(list(self.__selected_order_ids))
        self.__apply_totals_from_selection()

    async def __load_eligible_orders(self, customer_id: int, currency_id: int) -> list[OrderPlainSchema]:
        orders = await self.__perform_get_sales_orders(customer_id, currency_id)
        current_invoice_id = self._request_data.input_values.get("id")
        eligible: list[OrderPlainSchema] = []
        for order in orders:
            if order.invoice_id is not None and order.invoice_id != current_invoice_id:
                continue
            order_statuses = await self.__perform_get_order_statuses(order.id)
            if not order_statuses:
                continue
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            if latest_status.status_id in self.__eligible_status_ids:
                eligible.append(order)
        return eligible

    def __build_source_rows(self, orders: list[OrderPlainSchema]) -> list[tuple[int, list[object]]]:
        rows: list[tuple[int, list[object]]] = []
        for order in orders:
            rows.append(
                (
                    order.id,
                    [
                        order.number,
                        order.order_date.strftime("%Y-%m-%d"),
                        f"{order.total_gross:.2f}",
                    ],
                )
            )
        return rows

    def __build_target_rows(self) -> list[tuple[int, list[object]]]:
        rows: list[tuple[int, list[object]]] = []
        for order_id in self.__selected_order_ids:
            order = self.__orders_by_id.get(order_id)
            if not order:
                continue
            rows.append(
                (
                    order.id,
                    [
                        order.number,
                        order.order_date.strftime("%Y-%m-%d"),
                        f"{order.total_gross:.2f}",
                    ],
                )
            )
        return rows

    def __apply_totals_from_selection(self) -> None:
        total_net = 0.0
        total_vat = 0.0
        total_gross = 0.0
        total_discount = 0.0
        for order_id in self.__selected_order_ids:
            order = self.__orders_by_id.get(order_id)
            if not order:
                continue
            total_net += order.total_net
            total_vat += order.total_vat
            total_gross += order.total_gross
            total_discount += order.total_discount
        self._view.set_order_totals(
            {
                "total_net": round(total_net, 2),
                "total_vat": round(total_vat, 2),
                "total_gross": round(total_gross, 2),
                "total_discount": round(total_discount, 2),
            }
        )

    async def __handle_orders_save(self) -> None:
        if not self._view:
            return
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        for _, order_id in pending_targets:
            self.__selected_order_ids.add(order_id)
        self.__target_rows = self.__build_target_rows()
        self._view.set_target_rows(self.__target_rows)
        self._view.mark_source_orders_as_moved(list(self.__selected_order_ids))
        self._view.set_target_enabled(bool(self.__selected_order_ids))
        self.__apply_totals_from_selection()

    def __reset_orders(self, view: InvoiceView) -> None:
        self.__orders_by_id.clear()
        self.__selected_order_ids.clear()
        self.__target_rows = []
        view.set_source_rows([])
        view.set_target_rows([])
        view.set_source_enabled(False)
        view.set_target_enabled(False)
        view.set_order_totals(
            {
                "total_net": 0,
                "total_vat": 0,
                "total_gross": 0,
                "total_discount": 0,
            }
        )

    async def __generate_invoice_number(self, issue_date: date) -> str:
        sequence = await self.__get_next_invoice_sequence(issue_date)
        return self.__format_invoice_number(issue_date, sequence)

    async def __get_next_invoice_sequence(self, issue_date: date) -> int:
        try:
            response = await self._service.get_page(
                Endpoint.INVOICES,
                None,
                query_params={"issue_date": issue_date.isoformat(), "page": 1, "page_size": 1},
                body_params=None,
                module_id=self._module_id,
            )
        except Exception:
            self._logger.exception("Failed to fetch invoice count for date.")
            return 1
        if not response:
            return 1
        return max(1, response.total + 1)

    @staticmethod
    def __format_invoice_number(issue_date: date, sequence: int) -> str:
        date_part = issue_date.strftime("%Y/%m/%d")
        return f"{date_part}/{sequence:04d}"

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_create(
        self,
        service: InvoiceService,
        endpoint: Endpoint,
        payload: InvoiceStrictSchema,
    ) -> InvoicePlainSchema:
        response = await super()._perform_create(service, endpoint, payload)
        await self.__assign_invoice_to_orders(response.id)
        return response

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_update(
        self,
        id: int,
        service: InvoiceService,
        endpoint: Endpoint,
        payload: InvoiceStrictSchema,
    ) -> InvoicePlainSchema:
        response = await super()._perform_update(id, service, endpoint, payload)
        await self.__assign_invoice_to_orders(response.id)
        return response

    async def __assign_invoice_to_orders(self, invoice_id: int) -> None:
        if not self.__selected_order_ids:
            return
        payload = [
            OrderInvoiceBulkStrictSchema(id=order_id, invoice_id=invoice_id)
            for order_id in self.__selected_order_ids
        ]
        await self.__order_service.update_bulk(
            Endpoint.ORDER_UPDATE_BULK, None, None, payload, self._module_id
        )
