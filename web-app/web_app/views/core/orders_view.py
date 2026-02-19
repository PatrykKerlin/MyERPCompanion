from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles, OrdersViewStyles, TypographyStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.components.image_preview_dialog_component import ImagePreviewDialogComponent
from views.components.item_details_dialog_component import ItemDetailsDialogComponent

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

        self.__orders_list = ft.ListView(spacing=AppDimensions.SPACE_SM, expand=True)
        self.__status_list = ft.ListView(spacing=AppDimensions.SPACE_SM, expand=True)
        self.__items_list = ft.ListView(spacing=AppDimensions.SPACE_XS, expand=True)
        self.__order_meta_column = ft.Column(spacing=AppDimensions.SPACE_2XS, tight=True)
        self.__status_loading = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            content=ft.ProgressRing(
                width=AppDimensions.STATUS_LOADING_RING_SIZE,
                height=AppDimensions.STATUS_LOADING_RING_SIZE,
            ),
            padding=OrdersViewStyles.STATUS_LOADING_PADDING,
        )
        self.__download_invoice_button = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            tooltip=self._translation.get("download_invoice_pdf"),
            on_click=lambda _: self.__handle_download_invoice_clicked(),
            style=ButtonStyles.icon,
        )
        self.__download_invoice_placeholder = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            disabled=True,
            opacity=0.0,
            style=ButtonStyles.icon,
        )

        new_order_button = ft.Button(
            content=self._translation.get("create_order"),
            on_click=lambda _: self._controller.on_new_order_clicked(),
            style=ButtonStyles.primary_regular,
        )
        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(self._translation.get("browse_orders"), style=TypographyStyles.PAGE_TITLE),
                new_order_button,
            ],
        )
        payment_legend = ft.Container(
            padding=OrdersViewStyles.PAYMENT_LEGEND_PADDING,
            border=OrdersViewStyles.PAYMENT_LEGEND_BORDER,
            border_radius=OrdersViewStyles.PAYMENT_LEGEND_RADIUS,
            content=ft.Column(
                spacing=AppDimensions.SPACE_2XS,
                tight=True,
                controls=[
                    ft.Text(self._translation.get("payment_status_legend"), style=TypographyStyles.LEGEND_TITLE),
                    ft.Row(
                        spacing=AppDimensions.SPACE_XS,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(OrdersViewStyles.UNPAID_ICON, size=OrdersViewStyles.UNPAID_LEGEND_ICON_SIZE),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    self._translation.get("invoice_unpaid_before_due"),
                                    style=TypographyStyles.LEGEND_TEXT,
                                    no_wrap=False,
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=AppDimensions.SPACE_XS,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                size=OrdersViewStyles.OVERDUE_LEGEND_ICON_SIZE,
                                color=OrdersViewStyles.OVERDUE_COLOR,
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    self._translation.get("invoice_unpaid_overdue"),
                                    style=TypographyStyles.LEGEND_TEXT,
                                    no_wrap=False,
                                    color=OrdersViewStyles.OVERDUE_COLOR,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

        left_panel = ft.Container(
            expand=True,
            padding=OrdersViewStyles.PANEL_PADDING,
            border=OrdersViewStyles.PANEL_BORDER,
            border_radius=OrdersViewStyles.PANEL_RADIUS,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(self._translation.get("browse_orders"), style=TypographyStyles.SECTION_TITLE),
                    payment_legend,
                    self.__orders_list,
                ],
            ),
        )
        right_panel = ft.Container(
            expand=True,
            padding=OrdersViewStyles.PANEL_PADDING,
            border=OrdersViewStyles.PANEL_BORDER,
            border_radius=OrdersViewStyles.PANEL_RADIUS,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(self._translation.get("order_details"), style=TypographyStyles.SECTION_TITLE),
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
                                        ft.Text(self._translation.get("items"), style=TypographyStyles.SECTION_TITLE),
                                        self.__items_list,
                                    ],
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 4},
                                expand=True,
                                border=OrdersViewStyles.STATUS_COLUMN_BORDER,
                                padding=OrdersViewStyles.STATUS_COLUMN_PADDING,
                                content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Text(
                                            self._translation.get("status_history"),
                                            style=TypographyStyles.SECTION_TITLE,
                                        ),
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
            elevation=OrdersViewStyles.CARD_ELEVATION,
            bgcolor=OrdersViewStyles.CARD_BGCOLOR,
            content=ft.Container(
                expand=True,
                padding=OrdersViewStyles.CARD_PADDING,
                content=ft.Column(
                    expand=True,
                    spacing=AppDimensions.SPACE_LG,
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
        page = self.app_page
        viewport_width = page.width or page.window.width
        viewport_height = page.height or page.window.height
        if not viewport_width or not viewport_height:
            return
        self.__card.width = int(viewport_width * AppDimensions.CONTENT_WIDTH_RATIO)
        self.__card.height = int(viewport_height * AppDimensions.CONTENT_HEIGHT_RATIO)
        self._safe_update(self.__card)

    def __open_image_dialog(self, url: str) -> None:
        dialog = ImagePreviewDialogComponent(
            translation=self._translation, image_url=url, on_ok_clicked=lambda _: self.pop_dialog()
        )
        self.queue_dialog(dialog)

    def __open_item_dialog(self, item: dict[str, Any]) -> None:
        is_fragile = item.get("is_fragile")
        fragile_text = ""
        if is_fragile is not None:
            fragile_text = self._translation.get("yes") if bool(is_fragile) else self._translation.get("no")
        detail_rows: list[tuple[str, str]] = [
            ("name", str(item.get("name") or "")),
            ("index", str(item.get("index") or "")),
            ("ean", str(item.get("ean") or "")),
            ("description", str(item.get("description") or "")),
            ("is_fragile", fragile_text),
            ("expiration_date", str(item.get("expiration_date") or "")),
            ("category_name", str(item.get("category_name") or "")),
            ("available", str(item.get("available") or "")),
            ("vat_rate", str(item.get("vat_rate") or "")),
            ("moq", str(item.get("moq") or "")),
            ("dimensions", str(item.get("dimensions") or "")),
            ("weight", str(item.get("weight") or "")),
        ]
        raw_images = item.get("images")
        image_urls = [url for url in raw_images if isinstance(url, str)] if isinstance(raw_images, list) else []
        dialog = ItemDetailsDialogComponent(
            translation=self._translation,
            detail_rows=detail_rows,
            image_urls=image_urls,
            on_image_clicked=self.__open_image_dialog,
            on_ok_clicked=lambda _: self.pop_dialog(),
            safe_update=self._safe_update,
        )
        self.queue_dialog(dialog)

    def __register_card_resize_handler(self) -> None:
        page = self.app_page
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
            self._safe_update(self.__orders_list)
            return
        for order in self.__orders:
            order_id = order["id"]
            selected = order_id == self.__selected_order_id
            number = str(order.get("number") or "-")
            order_date = str(order.get("order_date") or "-")
            has_invoice = isinstance(order.get("invoice_id"), int)
            due_date = self.__parse_iso_date(order.get("invoice_due_date"))
            is_paid = order.get("invoice_is_paid")
            payment_status = self.__resolve_order_payment_status(
                has_invoice=has_invoice,
                due_date=due_date,
                is_paid=is_paid,
            )
            icon_control: ft.Control | None = None
            number_color: str | ft.Colors | None = None
            date_color: str | ft.Colors | None = None
            if payment_status == "unpaid":
                icon_control = ft.Icon(OrdersViewStyles.UNPAID_ICON, size=OrdersViewStyles.UNPAID_LIST_ICON_SIZE)
            elif payment_status == "overdue":
                icon_control = ft.Icon(
                    ft.Icons.WARNING_AMBER_ROUNDED,
                    size=OrdersViewStyles.OVERDUE_LIST_ICON_SIZE,
                    color=OrdersViewStyles.OVERDUE_COLOR,
                )
                number_color = OrdersViewStyles.OVERDUE_COLOR
                date_color = OrdersViewStyles.OVERDUE_COLOR
            item = ft.Container(
                padding=OrdersViewStyles.ORDER_TILE_PADDING,
                border=OrdersViewStyles.order_tile_border(selected),
                border_radius=OrdersViewStyles.ORDER_TILE_RADIUS,
                bgcolor=OrdersViewStyles.order_tile_bgcolor(selected),
                on_click=lambda _, oid=order_id: self._controller.on_order_selected(oid),
                content=ft.Row(
                    spacing=AppDimensions.SPACE_SM,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        number,
                                        style=TypographyStyles.SECTION_TITLE,
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
                            width=AppDimensions.ORDER_PAYMENT_ICON_SLOT_WIDTH,
                            height=AppDimensions.ORDER_PAYMENT_ICON_SLOT_HEIGHT,
                            alignment=ft.Alignment.CENTER,
                            content=icon_control,
                        ),
                    ],
                ),
            )
            self.__orders_list.controls.append(item)
        self._safe_update(self.__orders_list)

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
    def __resolve_order_payment_status(has_invoice: bool, due_date: date | None, is_paid: Any) -> str:
        if not has_invoice:
            return "none"
        if is_paid:
            return "none"
        if due_date and due_date < date.today():
            return "overdue"
        return "unpaid"

    def __render_status(self) -> None:
        self.__status_loading.visible = self.__is_status_loading
        self._safe_update(self.__status_loading)
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
        self._safe_update(self.__order_meta_column)

        self.__items_list.controls.clear()
        if self.__selected_order_id is None:
            self.__items_list.controls.append(ft.Text(self._translation.get("select_order")))
            self._safe_update(self.__items_list)
        elif not self.__order_items:
            self.__items_list.controls.append(ft.Text(self._translation.get("no_items")))
            self._safe_update(self.__items_list)
        else:
            self.__items_list.controls.append(
                ft.Container(
                    padding=OrdersViewStyles.ORDER_META_HEADER_PADDING,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        spacing=AppDimensions.SPACE_LG,
                        controls=[
                            ft.Container(
                                width=AppDimensions.ORDER_ITEMS_INDEX_COL_WIDTH,
                                content=ft.Text(
                                    self._translation.get("index"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    self._translation.get("name"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                width=AppDimensions.ORDER_ITEMS_EAN_COL_WIDTH,
                                content=ft.Text(
                                    self._translation.get("ean"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                width=AppDimensions.ORDER_ITEMS_QUANTITY_COL_WIDTH,
                                alignment=ft.Alignment.CENTER_RIGHT,
                                content=ft.Text(
                                    self._translation.get("quantity"),
                                    style=TypographyStyles.SECTION_TITLE,
                                    no_wrap=True,
                                ),
                            ),
                            ft.Container(width=AppDimensions.ORDER_ITEMS_GAP_COL_WIDTH),
                            ft.Container(
                                width=AppDimensions.ORDER_ITEMS_DISCOUNTS_COL_WIDTH,
                                content=ft.Text(
                                    self._translation.get("discounts"),
                                    style=TypographyStyles.SECTION_TITLE,
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
                        padding=OrdersViewStyles.ORDER_ITEMS_ROW_PADDING,
                        border=OrdersViewStyles.ORDER_ITEMS_ROW_BORDER,
                        border_radius=OrdersViewStyles.ORDER_ITEMS_ROW_RADIUS,
                        on_click=lambda _, item=row: self.__open_item_dialog(item),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            spacing=AppDimensions.SPACE_LG,
                            controls=[
                                ft.Container(
                                    width=AppDimensions.ORDER_ITEMS_INDEX_COL_WIDTH,
                                    content=ft.Text(item_index, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(item_name, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    width=AppDimensions.ORDER_ITEMS_EAN_COL_WIDTH,
                                    content=ft.Text(item_ean, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    width=AppDimensions.ORDER_ITEMS_QUANTITY_COL_WIDTH,
                                    alignment=ft.Alignment.CENTER_RIGHT,
                                    content=ft.Text(quantity, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(width=AppDimensions.ORDER_ITEMS_GAP_COL_WIDTH),
                                ft.Container(
                                    width=AppDimensions.ORDER_ITEMS_DISCOUNTS_COL_WIDTH,
                                    content=ft.Text(discounts, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                            ],
                        ),
                    )
                )
            self._safe_update(self.__items_list)

        self.__status_list.controls.clear()
        if self.__selected_order_id is None:
            self.__status_list.controls.append(ft.Text(self._translation.get("select_order")))
            self._safe_update(self.__status_list)
            return
        if not self.__status_history:
            self.__status_list.controls.append(ft.Text(self._translation.get("no_status_history")))
            self._safe_update(self.__status_list)
            return
        for row in self.__status_history:
            status = str(row.get("status") or "-")
            created_at = str(row.get("created_at") or "-")
            self.__status_list.controls.append(
                ft.Container(
                    padding=OrdersViewStyles.STATUS_ROW_PADDING,
                    border=OrdersViewStyles.STATUS_ROW_BORDER,
                    border_radius=OrdersViewStyles.STATUS_ROW_RADIUS,
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
        self._safe_update(self.__status_list)

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
                spacing=AppDimensions.SPACE_SM,
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
                    width=AppDimensions.ORDER_META_LABEL_COL_WIDTH,
                    content=ft.Text(
                        f"{label}:",
                        style=TypographyStyles.SECTION_TITLE_SEMIBOLD,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ),
                value_control,
            ],
            spacing=AppDimensions.SPACE_LG,
        )
