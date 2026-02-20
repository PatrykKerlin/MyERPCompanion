import asyncio
import os
import subprocess
from datetime import date, timedelta
from typing import Any, Callable, cast

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, SalesOrderStrictSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.base.base_service import BaseService
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
        self.__invoiced_status_id: int | None = None
        self.__orders_by_id: dict[int, OrderPlainSchema] = {}
        self.__selected_order_ids: set[int] = set()
        self.__pending_order_ids: set[int] = set()

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

    def on_generate_pdf_clicked(self, _: ft.Event[ft.Button]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_generate_pdf)

    def on_orders_delete_clicked(self, order_ids: list[int]) -> None:
        if not self._view or not order_ids:
            return
        self._page.run_task(self.__handle_orders_delete, order_ids)

    def on_create_mode_requested(self) -> None:
        self._page.run_task(self.__refresh_create_defaults)

    def on_read_mode_requested(self) -> None:
        self._page.run_task(self.__reload_orders_for_selection)

    def get_create_defaults(self) -> dict[str, Any]:
        return self.__build_create_defaults()

    def get_search_result_columns(self, available_fields: list[str]) -> list[str]:
        hidden_fields = {"currency_id", "customer_id"}
        return [field for field in available_fields if field not in hidden_fields]

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> InvoiceView:
        currencies, customers, statuses = await asyncio.gather(
            self.__perform_get_all_currencies(),
            self.__perform_get_all_customers(),
            self.__perform_get_all_statuses(),
        )
        self.__eligible_status_ids = {status.id for status in statuses if status.order == 4}
        invoiced_status = next((status for status in statuses if status.order == 5), None)
        self.__invoiced_status_id = invoiced_status.id if invoiced_status else None
        self.__prefetched_create_number = None
        view = InvoiceView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            currencies,
            customers,
            self.on_generate_pdf_clicked,
            self.on_orders_save_clicked,
            self.on_orders_delete_clicked,
        )
        self.__reset_orders(view)
        return view

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_create(
        self,
        service: BaseService[InvoicePlainSchema, InvoiceStrictSchema],
        endpoint: Endpoint,
        payload: InvoiceStrictSchema,
    ) -> InvoicePlainSchema:
        try:
            issue_date = payload.issue_date
        except Exception:
            issue_date = date.today()
        if not payload.number or payload.number == self.__prefetched_create_number:
            next_number = await self.__generate_invoice_number(issue_date)
            payload = payload.model_copy(update={"number": next_number})
        response = await self.__perform_create_invoice(payload)
        if response:
            await self.__assign_invoice_to_orders(response.id)
        return response

    async def _perform_update(
        self,
        id: int,
        service: BaseService[InvoicePlainSchema, InvoiceStrictSchema],
        endpoint: Endpoint,
        payload: InvoiceStrictSchema,
    ) -> InvoicePlainSchema:
        response = await self.__perform_update_invoice(id, payload)
        if response:
            await self.__assign_invoice_to_orders(response.id)
        return response

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
    async def __perform_get_invoices_by_issue_date(self, issue_date: date) -> list[InvoicePlainSchema]:
        return await self._service.get_all(
            Endpoint.INVOICES,
            None,
            {"issue_date": issue_date.isoformat()},
            None,
            self._module_id,
        )

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

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_invoice(self, payload: InvoiceStrictSchema) -> InvoicePlainSchema:
        return await self._service.create(Endpoint.INVOICES, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_invoice(self, invoice_id: int, payload: InvoiceStrictSchema) -> InvoicePlainSchema:
        return await self._service.update(Endpoint.INVOICES, invoice_id, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_download_invoice_pdf(self, invoice_id: int) -> tuple[bytes, str | None]:
        return await self._service.download_pdf(Endpoint.INVOICES_PDF, invoice_id, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_orders_by_ids(self, order_ids: list[int]) -> list[OrderPlainSchema]:
        if not order_ids:
            return []
        body_params = IdsPayloadSchema(ids=order_ids)
        return await self.__order_service.get_bulk(Endpoint.ORDERS_GET_BULK, None, None, body_params, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_orders_invoice_bulk(self, payload: list[SalesOrderStrictSchema]) -> None:
        await self.__order_service.update_bulk(
            Endpoint.ORDER_UPDATE_BULK,
            None,
            None,
            cast(list[Any], payload),
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_statuses_bulk(
        self, payload: list[AssocOrderStatusStrictSchema]
    ) -> list[AssocOrderStatusPlainSchema] | None:
        if not payload:
            return []
        return await self.__order_status_service.create_bulk(
            Endpoint.ORDER_STATUSES_CREATE_BULK, None, None, payload, self._module_id
        )

    def __build_create_defaults(self) -> dict[str, Any]:
        today = date.today()
        number = self.__prefetched_create_number or self.__format_invoice_number(today, 1)
        defaults: dict[str, Any] = {
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

    def __get_current_invoice_id(self) -> int | None:
        value = self._request_data.input_values.get("id")
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
        invoice_id = self.__get_current_invoice_id()
        pending_ids = self.__pending_order_ids if self._view.mode == ViewMode.CREATE else set()
        source_orders, target_orders = await self.__load_orders_for_selection(
            customer_id, currency_id, invoice_id, pending_ids
        )
        combined_orders = {order.id: order for order in (source_orders + target_orders)}
        self.__orders_by_id = combined_orders
        if self._view.mode == ViewMode.CREATE:
            self.__selected_order_ids = set(self.__pending_order_ids)
        else:
            self.__selected_order_ids = {order.id for order in target_orders}
        source_rows = self.__build_source_rows(source_orders)
        self._view.set_source_rows(source_rows)
        self._view.set_source_enabled(bool(source_rows))
        self._view.set_target_rows(self.__build_target_rows())
        self._view.set_target_enabled(bool(source_rows) or bool(self.__selected_order_ids))
        self._view.mark_source_orders_as_moved(list(self.__selected_order_ids))
        self.__apply_totals_from_selection()

    async def __load_orders_for_selection(
        self, customer_id: int, currency_id: int, invoice_id: int | None, pending_ids: set[int]
    ) -> tuple[list[OrderPlainSchema], list[OrderPlainSchema]]:
        orders = await self.__perform_get_sales_orders(customer_id, currency_id)
        sales_orders = [order for order in orders if order.is_sales is True]
        if pending_ids:
            target_orders = [order for order in sales_orders if order.id in pending_ids]
        else:
            target_orders = (
                [order for order in sales_orders if invoice_id is not None and order.invoice_id == invoice_id]
                if invoice_id is not None
                else []
            )
        source_candidates = [
            order for order in sales_orders if order.invoice_id is None and order.id not in pending_ids
        ]
        if not source_candidates:
            return [], target_orders
        status_tasks = {order.id: self.__perform_get_order_statuses(order.id) for order in source_candidates}
        status_results = await asyncio.gather(*status_tasks.values())
        order_statuses_by_id = {
            order_id: (statuses or []) for order_id, statuses in zip(status_tasks.keys(), status_results, strict=False)
        }
        source_orders: list[OrderPlainSchema] = []
        for order in source_candidates:
            order_statuses = order_statuses_by_id.get(order.id, [])
            if not order_statuses:
                continue
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            if latest_status.status_id in self.__eligible_status_ids:
                source_orders.append(order)
        return source_orders, target_orders

    def __build_source_rows(self, orders: list[OrderPlainSchema]) -> list[tuple[int, list[Any]]]:
        rows: list[tuple[int, list[Any]]] = []
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

    def __build_target_rows(self) -> list[tuple[int, list[Any]]]:
        rows: list[tuple[int, list[Any]]] = []
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
        if not self._view:
            return
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
        invoice_id = self.__get_current_invoice_id()
        if self._view.mode == ViewMode.CREATE or invoice_id is None:
            self.__pending_order_ids.update(order_id for _, order_id in pending_targets)
            await self.__reload_orders_for_selection()
            return
        if invoice_id is not None:
            pending_order_ids = [order_id for _, order_id in pending_targets]
            if pending_order_ids:
                await self.__update_orders_invoice_assignment(pending_order_ids, invoice_id)
        await self.__reload_orders_for_selection()

    async def __handle_orders_delete(self, order_ids: list[int]) -> None:
        if not self._view or not order_ids:
            return
        if self._view.mode == ViewMode.CREATE or self.__get_current_invoice_id() is None:
            for order_id in order_ids:
                self.__pending_order_ids.discard(order_id)
            await self.__reload_orders_for_selection()
            return
        invoice_id = self.__get_current_invoice_id()
        if invoice_id is not None:
            await self.__update_orders_invoice_assignment(order_ids, None)
        await self.__reload_orders_for_selection()

    async def __handle_generate_pdf(self) -> None:
        if not self._view or self._view.mode not in {ViewMode.READ, ViewMode.EDIT}:
            return
        invoice_id = self.__get_current_invoice_id()
        if invoice_id is None:
            return
        pdf_result = await self.__perform_download_invoice_pdf(invoice_id)
        if pdf_result is None:
            return
        content, suggested_name = pdf_result
        default_name = suggested_name or f"invoice_{invoice_id}.pdf"
        file_path = await self.__pick_pdf_save_path(default_name)
        if not file_path:
            return
        try:
            await asyncio.to_thread(self.__write_pdf_file, file_path, content)
        except Exception:
            self._logger.exception(f"Unhandled exception in {self.__handle_generate_pdf.__qualname__}")
            self._open_error_dialog(message_key=ApiActionError.GENERIC)

    async def __pick_pdf_save_path(self, suggested_name: str) -> str | None:
        try:
            selected_path = await asyncio.to_thread(self.__pick_linux_save_path, suggested_name)
            if not selected_path:
                return None
            if not selected_path.lower().endswith(".pdf"):
                return f"{selected_path}.pdf"
            return selected_path
        except Exception:
            self._logger.exception(f"Unhandled exception in {self.__pick_pdf_save_path.__qualname__}")
            self._open_error_dialog(message_key=ApiActionError.GENERIC)
            return None

    def __pick_linux_save_path(self, suggested_name: str) -> str | None:
        translation = self._state_store.app_state.translation.items
        cwd = os.getcwd()
        env = os.environ.copy()
        env["WAYLAND_DISPLAY"] = env.get("WAYLAND_DISPLAY", "wayland-0")
        env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", "/mnt/wslg/runtime-dir")
        env["XDG_SESSION_TYPE"] = "wayland"
        env["GDK_BACKEND"] = "wayland"
        args = [
            "zenity",
            "--file-selection",
            "--save",
            "--confirm-overwrite",
            f"--title={translation.get('save_pdf')}",
            f"--filename={os.path.join(cwd, suggested_name)}",
            "--file-filter=PDF files | *.pdf",
        ]
        result = subprocess.run(args, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                self._logger.warning(
                    f"Zenity save dialog returned non-zero code with stderr: {stderr}",
                )
            return None
        return result.stdout.strip() or None

    @staticmethod
    def __write_pdf_file(file_path: str, content: bytes) -> None:
        with open(file_path, "wb") as file:
            file.write(content)

    def __reset_orders(self, view: InvoiceView) -> None:
        self.__orders_by_id.clear()
        self.__selected_order_ids.clear()
        self.__pending_order_ids.clear()
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

    async def __update_orders_invoice_assignment(self, order_ids: list[int], invoice_id: int | None) -> None:
        orders = await self.__perform_get_orders_by_ids(order_ids)
        if not orders:
            return
        payload = [self.__build_order_update_payload(order, invoice_id) for order in orders]
        await self.__perform_update_orders_invoice_bulk(payload)
        if invoice_id is not None:
            await self.__update_orders_invoiced_status(order_ids)

    @staticmethod
    def __build_order_update_payload(order: OrderPlainSchema, invoice_id: int | None) -> SalesOrderStrictSchema:
        if order.customer_id is None or order.delivery_method_id is None:
            raise ValueError("Order is missing required sales fields for invoice assignment.")
        return SalesOrderStrictSchema(
            id=order.id,
            number=order.number,
            is_sales=True,
            total_net=order.total_net,
            total_vat=order.total_vat,
            total_gross=order.total_gross,
            total_discount=order.total_discount,
            order_date=order.order_date,
            tracking_number=order.tracking_number,
            shipping_cost=order.shipping_cost,
            notes=order.notes,
            external_notes=order.external_notes,
            customer_id=order.customer_id,
            supplier_id=order.supplier_id,
            delivery_method_id=order.delivery_method_id,
            currency_id=order.currency_id,
            invoice_id=invoice_id,
        )

    async def __refresh_create_defaults(self) -> None:
        if not self._view or self._view.mode != ViewMode.CREATE:
            return
        issue_date = date.today()
        number = await self.__generate_invoice_number(issue_date)
        self.__prefetched_create_number = number
        self._view.set_number(number)
        self._view.set_issue_date(issue_date)
        self._view.set_due_date(issue_date)

    async def __get_next_invoice_sequence(self, issue_date: date) -> int:
        invoices = await self.__perform_get_invoices_by_issue_date(issue_date)
        max_sequence = 0
        for invoice in invoices or []:
            if invoice.issue_date != issue_date:
                continue
            number = (invoice.number or "").strip()
            parts = [part for part in number.split("/") if part]
            if not parts:
                continue
            suffix = parts[-1]
            if not suffix.isdigit():
                continue
            max_sequence = max(max_sequence, int(suffix))
        return max(1, max_sequence + 1)

    @staticmethod
    def __format_invoice_number(issue_date: date, sequence: int) -> str:
        date_part = issue_date.strftime("%Y/%m/%d")
        return f"{date_part}/{sequence:04d}"

    async def __assign_invoice_to_orders(self, invoice_id: int) -> None:
        if not self.__selected_order_ids:
            return
        await self.__update_orders_invoice_assignment(list(self.__selected_order_ids), invoice_id)
        self.__pending_order_ids.clear()

    async def __update_orders_invoiced_status(self, order_ids: list[int]) -> None:
        if not order_ids:
            return
        status_id = self.__invoiced_status_id
        if status_id is None:
            self._logger.warning("Missing invoiced status, skipping order status update.")
            return
        status_results = await asyncio.gather(*(self.__perform_get_order_statuses(order_id) for order_id in order_ids))
        payload: list[AssocOrderStatusStrictSchema] = []
        for order_id, statuses in zip(order_ids, status_results, strict=False):
            latest_status_id = self.__get_latest_status_id(statuses or [])
            if latest_status_id == status_id:
                continue
            payload.append(AssocOrderStatusStrictSchema(order_id=order_id, status_id=status_id))
        if not payload:
            return
        await self.__perform_create_order_statuses_bulk(payload)

    @staticmethod
    def __get_latest_status_id(statuses: list[AssocOrderStatusPlainSchema]) -> int | None:
        if not statuses:
            return None
        latest = max(statuses, key=lambda status: (status.created_at, status.id))
        return latest.status_id
