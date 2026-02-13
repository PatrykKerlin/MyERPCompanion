from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.orders_controller import OrdersController


class OrdersView(BaseView["OrdersController"]):
    def __init__(
        self,
        controller: OrdersController,
        translation: Translation,
        orders: list[dict[str, Any]],
        selected_order_id: int | None,
        selected_invoice_id: int | None,
        order_meta: dict[str, str],
        order_items: list[dict[str, Any]],
        status_history: list[dict[str, str]],
    ) -> None:
        super().__init__(
            controller=controller,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=View.WEB_ORDERS,
            data_row=None,
            base_label_size=0,
            base_input_size=0,
            base_columns_qty=12,
        )
        self.__orders = list(orders)
        self.__selected_order_id = selected_order_id
        self.__selected_invoice_id = selected_invoice_id
        self.__order_meta = dict(order_meta)
        self.__order_items = list(order_items)
        self.__status_history = list(status_history)
        self.__is_status_loading = False
        self.__card: ft.Card | None = None
        self.__card_resize_handler: Callable[[ft.ControlEvent], None] | None = None

        self.__orders_list = ft.ListView(spacing=8, expand=True)
        self.__status_list = ft.ListView(spacing=8, expand=True)
        self.__items_list = ft.ListView(spacing=6, expand=True)
        self.__order_meta_column = ft.Column(spacing=2, tight=True)
        self.__status_loading = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            content=ft.ProgressRing(width=20, height=20),
            padding=ft.Padding.only(bottom=8),
        )
        self.__download_invoice_button = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            tooltip=self._translation.get("download_invoice_pdf"),
            on_click=lambda _: self.__handle_download_invoice_clicked(),
        )
        self.__download_invoice_placeholder = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            disabled=True,
            opacity=0.0,
        )

        new_order_button = ft.Button(
            content=self._translation.get("create_order"),
            on_click=lambda _: self._controller.on_new_order_clicked(),
        )
        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(self._translation.get("browse_orders"), size=26, weight=ft.FontWeight.BOLD),
                new_order_button,
            ],
        )
        payment_legend = ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=6),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            content=ft.Column(
                spacing=4,
                tight=True,
                controls=[
                    ft.Text(self._translation.get("payment_status_legend"), size=11, weight=ft.FontWeight.W_600),
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.PENDING, size=16),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    self._translation.get("invoice_unpaid_before_due"),
                                    size=11,
                                    no_wrap=False,
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=ft.Colors.ERROR),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    self._translation.get("invoice_unpaid_overdue"),
                                    size=11,
                                    no_wrap=False,
                                    color=ft.Colors.ERROR,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

        left_panel = ft.Container(
            expand=True,
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(self._translation.get("browse_orders"), weight=ft.FontWeight.BOLD),
                    payment_legend,
                    self.__orders_list,
                ],
            ),
        )
        right_panel = ft.Container(
            expand=True,
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(self._translation.get("order_details"), weight=ft.FontWeight.BOLD),
                    self.__order_meta_column,
                    ft.Divider(),
                    ft.ResponsiveRow(
                        columns=12,
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            ft.Container(
                                col={"sm": 12, "md": 8},
                                expand=True,
                                content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Text(self._translation.get("items"), weight=ft.FontWeight.BOLD),
                                        self.__items_list,
                                    ],
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 4},
                                expand=True,
                                content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Text(self._translation.get("status_history"), weight=ft.FontWeight.BOLD),
                                        self.__status_loading,
                                        self.__status_list,
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
        panels_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                ft.Container(col={"sm": 12, "md": 2}, content=left_panel, expand=True),
                ft.Container(col={"sm": 12, "md": 10}, content=right_panel, expand=True),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        )
        self.__card = ft.Card(
            elevation=2,
            content=ft.Container(
                expand=True,
                padding=ft.Padding.all(16),
                content=ft.Column(
                    expand=True,
                    spacing=12,
                    controls=[header_row, panels_row],
                ),
            ),
        )
        self.content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=self.__card,
        )
        self.__apply_card_size()
        self.__register_card_resize_handler()
        self.__render_orders()
        self.__render_status()

    def set_selected_order(self, order_id: int) -> None:
        self.__selected_order_id = order_id
        self.__render_orders()

    def set_status_history(
        self,
        order_meta: dict[str, str],
        order_items: list[dict[str, Any]],
        status_history: list[dict[str, str]],
        selected_invoice_id: int | None,
    ) -> None:
        self.__order_meta = dict(order_meta)
        self.__order_items = list(order_items)
        self.__status_history = list(status_history)
        self.__selected_invoice_id = selected_invoice_id
        self.__render_status()

    def set_status_loading(self, loading: bool) -> None:
        self.__is_status_loading = loading
        self.__render_status()

    def __apply_card_size(self) -> None:
        if not self.__card:
            return
        page = self._controller._page
        viewport_width = page.width or page.window.width
        viewport_height = page.height or page.window.height
        if not viewport_width or not viewport_height:
            return
        self.__card.width = int(viewport_width * 0.75)
        self.__card.height = int(viewport_height * 0.75)
        self.__safe_update(self.__card)

    def __open_image_dialog(self, url: str) -> None:
        dialog = BaseDialog(
            title=None,
            controls=[ft.Image(src=url, width=800, height=800, fit=ft.BoxFit.CONTAIN)],
            actions=[
                ft.TextButton(self._translation.get("ok"), on_click=lambda _: self._controller._page.pop_dialog()),
            ],
        )
        self._controller._queue_dialog(dialog)

    def __open_item_dialog(self, item: dict[str, Any]) -> None:
        is_fragile = item.get("is_fragile")
        detail_rows: list[tuple[str, str]] = [
            ("name", str(item.get("name") or "")),
            ("index", str(item.get("index") or "")),
            ("ean", str(item.get("ean") or "")),
            ("description", str(item.get("description") or "")),
            (
                "is_fragile",
                (
                    ""
                    if is_fragile is None
                    else self._translation.get("yes") if bool(is_fragile) else self._translation.get("no")
                ),
            ),
            ("expiration_date", str(item.get("expiration_date") or "")),
            ("category_name", str(item.get("category_name") or "")),
            ("available", str(item.get("available") or "")),
            ("vat_rate", str(item.get("vat_rate") or "")),
            ("moq", str(item.get("moq") or "")),
            ("dimensions", str(item.get("dimensions") or "")),
            ("weight", str(item.get("weight") or "")),
        ]
        labels_column = ft.Column(
            controls=[ft.Text(self._translation.get(key)) for key, _ in detail_rows],
            tight=True,
        )
        values_column = ft.Column(
            controls=[ft.Text(value) for _, value in detail_rows],
            tight=True,
            expand=True,
        )
        raw_images = item.get("images")
        image_urls = [url for url in raw_images if isinstance(url, str)] if isinstance(raw_images, list) else []
        gallery_row: ft.Control | None
        if image_urls:
            start_index = 0
            thumbnails_row = ft.Row(spacing=8, run_spacing=8)

            def update_buttons() -> None:
                left_button.disabled = start_index <= 0
                right_button.disabled = start_index + 3 >= len(image_urls)
                self.__safe_update(left_button)
                self.__safe_update(right_button)

            def render_thumbnails() -> None:
                thumbnails_row.controls.clear()
                window = image_urls[start_index : start_index + 3]
                for url in window:
                    thumbnails_row.controls.append(
                        ft.Container(
                            content=ft.Image(src=url, width=96, height=96, fit=ft.BoxFit.CONTAIN),
                            on_click=lambda _, u=url: self.__open_image_dialog(u),
                        )
                    )
                self.__safe_update(thumbnails_row)
                update_buttons()

            def move_left() -> None:
                nonlocal start_index
                if start_index <= 0:
                    return
                start_index -= 1
                render_thumbnails()

            def move_right() -> None:
                nonlocal start_index
                if start_index + 3 >= len(image_urls):
                    return
                start_index += 1
                render_thumbnails()

            left_button = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=lambda: move_left(), disabled=True)
            right_button = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=lambda: move_right(), disabled=True)
            render_thumbnails()
            gallery_row = ft.Row(controls=[left_button, thumbnails_row, right_button], spacing=8)
        else:
            gallery_row = ft.Container(
                content=ft.Text(self._translation.get("no_images")),
                padding=8,
            )
        controls: list[ft.Control] = [ft.Row(controls=[labels_column, values_column], spacing=16, expand=True)]
        controls.append(gallery_row)
        dialog = BaseDialog(
            title=self._translation.get("item_details"),
            controls=controls,
            actions=[
                ft.TextButton(self._translation.get("ok"), on_click=lambda _: self._controller._page.pop_dialog()),
            ],
        )
        self._controller._queue_dialog(dialog)

    def __register_card_resize_handler(self) -> None:
        page = self._controller._page
        if self.__card_resize_handler is not None:
            return
        previous_handler = getattr(page, "on_resize", None)

        def handle_resize(event: ft.ControlEvent) -> None:
            if callable(previous_handler):
                previous_handler(event)
            self.__apply_card_size()

        self.__card_resize_handler = handle_resize
        setattr(page, "on_resize", handle_resize)

    def __render_orders(self) -> None:
        self.__orders_list.controls.clear()
        if not self.__orders:
            self.__orders_list.controls.append(ft.Text(self._translation.get("no_orders")))
            self.__safe_update(self.__orders_list)
            return
        for order in self.__orders:
            order_id = order.get("id")
            if not isinstance(order_id, int):
                continue
            selected = order_id == self.__selected_order_id
            number = str(order.get("number") or "-")
            order_date = str(order.get("order_date") or "-")
            due_date = self.__parse_iso_date(order.get("invoice_due_date"))
            is_paid = order.get("invoice_is_paid")
            payment_status = self.__resolve_order_payment_status(due_date=due_date, is_paid=is_paid)
            icon_control: ft.Control | None = None
            number_color: str | ft.Colors | None = None
            date_color: str | ft.Colors | None = None
            if payment_status == "unpaid":
                icon_control = ft.Icon(ft.Icons.PENDING, size=22)
            elif payment_status == "overdue":
                icon_control = ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=22, color=ft.Colors.ERROR)
                number_color = ft.Colors.ERROR
                date_color = ft.Colors.ERROR
            item = ft.Container(
                padding=ft.Padding.all(10),
                border=ft.Border.all(1, ft.Colors.PRIMARY if selected else ft.Colors.OUTLINE_VARIANT),
                border_radius=8,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if selected else None,
                on_click=lambda _, oid=order_id: self._controller.on_order_selected(oid),
                content=ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        number,
                                        weight=ft.FontWeight.BOLD,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        color=number_color,
                                    ),
                                    ft.Text(
                                        f"{self._translation.get('order_date')}: {order_date}",
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        color=date_color,
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            width=28,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            content=icon_control,
                        ),
                    ],
                ),
            )
            self.__orders_list.controls.append(item)
        self.__safe_update(self.__orders_list)

    @staticmethod
    def __parse_iso_date(raw: Any) -> date | None:
        if isinstance(raw, date):
            return raw
        if isinstance(raw, str):
            try:
                return date.fromisoformat(raw)
            except ValueError:
                return None
        return None

    @staticmethod
    def __resolve_order_payment_status(due_date: date | None, is_paid: Any) -> str:
        if not isinstance(is_paid, bool):
            return "none"
        if is_paid:
            return "none"
        if due_date and due_date < date.today():
            return "overdue"
        return "unpaid"

    def __render_status(self) -> None:
        self.__status_loading.visible = self.__is_status_loading
        self.__safe_update(self.__status_loading)
        self.__order_meta_column.controls.clear()
        if self.__selected_order_id is None:
            self.__order_meta_column.controls.append(ft.Text(self._translation.get("select_order")))
        elif self.__order_meta:
            has_invoice = isinstance(self.__selected_invoice_id, int)
            detail_rows: list[tuple[str, str]] = [
                (self._translation.get("number"), self.__order_meta.get("number", "-")),
                (self._translation.get("order_date"), self.__order_meta.get("order_date", "-")),
                (self._translation.get("currency"), self.__order_meta.get("currency", "-")),
                (self._translation.get("delivery_method"), self.__order_meta.get("delivery_method", "-")),
                (self._translation.get("customer_discount"), self.__order_meta.get("customer_discount", "-")),
                (self._translation.get("total_net"), self.__order_meta.get("total_net", "0.00")),
                (self._translation.get("total_vat"), self.__order_meta.get("total_vat", "0.00")),
                (self._translation.get("total_gross"), self.__order_meta.get("total_gross", "0.00")),
                (self._translation.get("total_discount"), self.__order_meta.get("total_discount", "0.00")),
                (self._translation.get("shipping_cost"), self.__order_meta.get("shipping_cost", "0.00")),
                (
                    self._translation.get("total_with_shipping"),
                    self.__order_meta.get("total_with_shipping", "0.00"),
                ),
            ]
            invoice_number = self.__order_meta.get("invoice_number")
            for label, value in detail_rows:
                self.__order_meta_column.controls.append(self.__build_order_meta_row(label=label, value=value))
            self.__download_invoice_button.disabled = not has_invoice
            invoice_trailing_control: ft.Control = (
                self.__download_invoice_button if has_invoice else self.__download_invoice_placeholder
            )
            self.__order_meta_column.controls.append(
                self.__build_order_meta_row(
                    label=self._translation.get("invoice_number"),
                    value=invoice_number if invoice_number else "-",
                    trailing_control=invoice_trailing_control,
                )
            )
        self.__safe_update(self.__order_meta_column)

        self.__items_list.controls.clear()
        if self.__selected_order_id is None:
            self.__items_list.controls.append(ft.Text(self._translation.get("select_order")))
            self.__safe_update(self.__items_list)
        elif not self.__order_items:
            self.__items_list.controls.append(ft.Text(self._translation.get("no_items")))
            self.__safe_update(self.__items_list)
        else:
            self.__items_list.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=8),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=110,
                                content=ft.Text(
                                    self._translation.get("index"), weight=ft.FontWeight.BOLD, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(self._translation.get("name"), weight=ft.FontWeight.BOLD, no_wrap=True),
                            ),
                            ft.Container(
                                width=130,
                                content=ft.Text(self._translation.get("ean"), weight=ft.FontWeight.BOLD, no_wrap=True),
                            ),
                            ft.Container(
                                width=90,
                                alignment=ft.Alignment.CENTER_RIGHT,
                                content=ft.Text(
                                    self._translation.get("quantity"),
                                    weight=ft.FontWeight.BOLD,
                                    no_wrap=True,
                                ),
                            ),
                            ft.Container(width=20),
                            ft.Container(
                                width=220,
                                content=ft.Text(
                                    self._translation.get("discounts"),
                                    weight=ft.FontWeight.BOLD,
                                    no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                )
            )
            for row in self.__order_items:
                item_index = str(row.get("index") or "-")
                item_name = str(row.get("name") or "-")
                item_ean = str(row.get("ean") or "-")
                quantity = str(row.get("quantity") or "0")
                discounts = str(row.get("discounts") or "-")
                self.__items_list.controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=6,
                        on_click=lambda _, item=row: self.__open_item_dialog(item),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=110,
                                    content=ft.Text(item_index, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(item_name, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    width=130,
                                    content=ft.Text(item_ean, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    width=90,
                                    alignment=ft.Alignment.CENTER_RIGHT,
                                    content=ft.Text(quantity, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(width=20),
                                ft.Container(
                                    width=220,
                                    content=ft.Text(discounts, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                            ],
                        ),
                    )
                )
            self.__safe_update(self.__items_list)

        self.__status_list.controls.clear()
        if self.__selected_order_id is None:
            self.__status_list.controls.append(ft.Text(self._translation.get("select_order")))
            self.__safe_update(self.__status_list)
            return
        if not self.__status_history:
            self.__status_list.controls.append(ft.Text(self._translation.get("no_status_history")))
            self.__safe_update(self.__status_list)
            return
        for row in self.__status_history:
            status = str(row.get("status") or "-")
            created_at = str(row.get("created_at") or "-")
            self.__status_list.controls.append(
                ft.Container(
                    padding=ft.Padding.all(8),
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=6,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(status, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(created_at, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                    ),
                )
            )
        self.__safe_update(self.__status_list)

    def __handle_download_invoice_clicked(self) -> None:
        self._controller.on_download_invoice_clicked(self.__selected_invoice_id)

    @staticmethod
    def __build_order_meta_row(
        label: str,
        value: str,
        trailing_control: ft.Control | None = None,
    ) -> ft.Row:
        if trailing_control is not None:
            value_control: ft.Control = ft.Row(
                spacing=8,
                controls=[
                    ft.Text(str(value), no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                    trailing_control,
                ],
            )
        else:
            value_control = ft.Container(
                expand=True,
                content=ft.Text(str(value), no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
            )
        return ft.Row(
            controls=[
                ft.Container(
                    width=220,
                    content=ft.Text(
                        f"{label}:",
                        weight=ft.FontWeight.W_600,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ),
                value_control,
            ],
            spacing=12,
        )

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        control.update()
