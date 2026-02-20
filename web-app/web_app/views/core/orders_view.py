from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles, OrdersViewStyles, TypographyStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_view import BaseView
from views.components.image_preview_dialog_component import ImagePreviewDialogComponent
from views.components.item_details_dialog_component import ItemDetailsDialogComponent

if TYPE_CHECKING:
    from controllers.core.orders_controller import OrdersController


class OrdersView(BaseView[OrdersController]):
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

        self.__orders_list = ft.ListView(spacing=AppDimensions.SPACE_SM, expand=True)
        self.__status_list = ft.ListView(spacing=AppDimensions.SPACE_SM, expand=True)
        self.__items_list = ft.ListView(spacing=AppDimensions.SPACE_XS, expand=True)
        self.__order_meta_column = ft.Column(
            spacing=AppDimensions.SPACE_2XS,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.__external_notes_column = ft.Column(
            spacing=AppDimensions.SPACE_2XS,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.__status_loading = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            content=ft.ProgressRing(),
            padding=OrdersViewStyles.STATUS_LOADING_PADDING,
        )
        self.__download_invoice_button = self._get_icon_button(
            icon=ft.Icons.DOWNLOAD,
            tooltip=self._translation.get("download_invoice_pdf"),
            on_click=lambda _: self.__handle_download_invoice_clicked(),
            style=ButtonStyles.icon,
        )
        self.__download_invoice_placeholder = self._get_icon_button(
            icon=ft.Icons.DOWNLOAD,
            disabled=True,
            style=ButtonStyles.icon,
            opacity=0.0,
        )

        new_order_button = self._get_button(
            content=self._translation.get("create_order"),
            on_click=lambda _: self._controller.on_new_order_clicked(),
            style=ButtonStyles.primary_regular,
        )
        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self._get_label(self._translation.get("browse_orders"), style=TypographyStyles.PAGE_TITLE),
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
                    self._get_label(
                        self._translation.get("payment_status_legend"), style=TypographyStyles.LEGEND_TITLE
                    ),
                    ft.Row(
                        spacing=AppDimensions.SPACE_XS,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(OrdersViewStyles.UNPAID_ICON, size=OrdersViewStyles.UNPAID_LEGEND_ICON_SIZE),
                            ft.Container(
                                expand=True,
                                content=self._get_label(
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
                                content=self._get_label(
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
                    self._get_label(self._translation.get("browse_orders"), style=TypographyStyles.SECTION_TITLE),
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
                    ft.Container(
                        expand=OrdersViewStyles.META_AND_NOTES_SECTION_EXPAND,
                        content=ft.ResponsiveRow(
                            columns=OrdersViewStyles.META_AND_NOTES_ROW_COLUMNS,
                            spacing=OrdersViewStyles.META_AND_NOTES_ROW_SPACING,
                            vertical_alignment=OrdersViewStyles.META_AND_NOTES_ROW_VERTICAL_ALIGNMENT,
                            controls=[
                                ft.Container(
                                    col=OrdersViewStyles.META_CONTAINER_COL,
                                    expand=True,
                                    content=ft.Column(
                                        expand=True,
                                        controls=[
                                            self._get_label(
                                                self._translation.get("order_details"),
                                                style=TypographyStyles.SECTION_TITLE,
                                            ),
                                            self.__order_meta_column,
                                        ],
                                    ),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.NOTES_CONTAINER_COL,
                                    expand=True,
                                    border=OrdersViewStyles.STATUS_COLUMN_BORDER,
                                    padding=OrdersViewStyles.NOTES_CONTAINER_PADDING,
                                    content=ft.Column(
                                        expand=True,
                                        controls=[
                                            self._get_label(
                                                self._translation.get("notes"),
                                                style=TypographyStyles.SECTION_TITLE,
                                            ),
                                            self.__external_notes_column,
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Divider(),
                    ft.Container(
                        expand=OrdersViewStyles.DETAILS_SECTION_EXPAND,
                        content=ft.ResponsiveRow(
                            columns=OrdersViewStyles.DETAILS_ROW_COLUMNS,
                            expand=True,
                            vertical_alignment=OrdersViewStyles.DETAILS_ROW_VERTICAL_ALIGNMENT,
                            controls=[
                                ft.Container(
                                    col=OrdersViewStyles.DETAILS_ITEMS_COL,
                                    expand=True,
                                    content=ft.Column(
                                        expand=True,
                                        controls=[
                                            self._get_label(
                                                self._translation.get("items"), style=TypographyStyles.SECTION_TITLE
                                            ),
                                            self.__items_list,
                                        ],
                                    ),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.DETAILS_STATUS_COL,
                                    expand=True,
                                    border=OrdersViewStyles.STATUS_COLUMN_BORDER,
                                    padding=OrdersViewStyles.STATUS_COLUMN_PADDING,
                                    content=ft.Column(
                                        expand=True,
                                        controls=[
                                            self._get_label(
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
                    ),
                ],
            ),
        )
        panels_row = ft.ResponsiveRow(
            columns=OrdersViewStyles.PANELS_ROW_COLUMNS,
            controls=[
                ft.Container(col=OrdersViewStyles.PANELS_LEFT_COL, content=left_panel, expand=True),
                ft.Container(col=OrdersViewStyles.PANELS_RIGHT_COL, content=right_panel, expand=True),
            ],
            alignment=OrdersViewStyles.PANELS_ROW_ALIGNMENT,
            vertical_alignment=OrdersViewStyles.PANELS_ROW_VERTICAL_ALIGNMENT,
            expand=True,
        )
        self.__card = ft.Card(
            expand=True,
            elevation=OrdersViewStyles.CARD_ELEVATION,
            bgcolor=OrdersViewStyles.CARD_BGCOLOR,
            content=ft.Container(
                expand=True,
                padding=OrdersViewStyles.CARD_PADDING,
                content=ft.Column(
                    expand=True,
                    spacing=OrdersViewStyles.CARD_CONTENT_SPACING,
                    controls=[header_row, panels_row],
                ),
            ),
        )
        self.content = ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            padding=OrdersViewStyles.CARD_OUTER_PADDING,
            content=ft.ResponsiveRow(
                columns=OrdersViewStyles.ROOT_ROW_COLUMNS,
                alignment=OrdersViewStyles.ROOT_ROW_ALIGNMENT,
                controls=[
                    ft.Container(
                        col=OrdersViewStyles.CARD_COL,
                        content=self.__card,
                        expand=True,
                    )
                ],
            ),
        )
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

    def __render_orders(self) -> None:
        self.__orders_list.controls.clear()
        if not self.__orders:
            self.__orders_list.controls.append(self._get_label(self._translation.get("no_orders")))
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
            if icon_control is None:
                icon_control = ft.Icon(
                    OrdersViewStyles.UNPAID_ICON,
                    size=OrdersViewStyles.UNPAID_LIST_ICON_SIZE,
                    opacity=0.0,
                )
            item = ft.Container(
                padding=OrdersViewStyles.ORDER_TILE_PADDING,
                border=OrdersViewStyles.order_tile_border(selected),
                border_radius=OrdersViewStyles.ORDER_TILE_RADIUS,
                bgcolor=OrdersViewStyles.order_tile_bgcolor(selected),
                on_click=lambda _, oid=order_id: self._controller.on_order_selected(oid),
                content=ft.ResponsiveRow(
                    columns=OrdersViewStyles.ORDER_TILE_ROW_COLUMNS,
                    spacing=OrdersViewStyles.ORDER_TILE_ROW_SPACING,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            col=OrdersViewStyles.ORDER_TILE_TEXT_COL,
                            content=ft.Column(
                                spacing=OrdersViewStyles.ORDER_TILE_TEXT_SPACING,
                                controls=[
                                    self._get_label(
                                        number,
                                        style=TypographyStyles.SECTION_TITLE,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        color=number_color,
                                    ),
                                    self._get_label(
                                        order_date,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        color=date_color,
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            col=OrdersViewStyles.ORDER_TILE_ICON_COL,
                            alignment=ft.Alignment.CENTER_RIGHT,
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
        self.__external_notes_column.controls.clear()
        if self.__selected_order_id is None:
            self.__order_meta_column.controls.append(self._get_label(self._translation.get("select_order")))
            self.__external_notes_column.controls.append(self._get_label(self._translation.get("select_order")))
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
            external_notes = str(self.__order_meta.get("external_notes") or "-")
            self.__external_notes_column.controls.append(self._get_label(external_notes, no_wrap=False))
        else:
            self.__external_notes_column.controls.append(self._get_label("-"))
        self._safe_update(self.__order_meta_column)
        self._safe_update(self.__external_notes_column)

        self.__items_list.controls.clear()
        if self.__selected_order_id is None:
            self.__items_list.controls.append(self._get_label(self._translation.get("select_order")))
            self._safe_update(self.__items_list)
        elif not self.__order_items:
            self.__items_list.controls.append(self._get_label(self._translation.get("no_items")))
            self._safe_update(self.__items_list)
        else:
            self.__items_list.controls.append(
                ft.Container(
                    padding=OrdersViewStyles.ORDER_META_HEADER_PADDING,
                    content=ft.ResponsiveRow(
                        columns=OrdersViewStyles.ITEMS_HEADER_ROW_COLUMNS,
                        alignment=OrdersViewStyles.ITEMS_HEADER_ROW_ALIGNMENT,
                        spacing=OrdersViewStyles.ITEMS_HEADER_ROW_SPACING,
                        controls=[
                            ft.Container(
                                col=OrdersViewStyles.ORDER_ITEM_INDEX_COL,
                                content=self._get_label(
                                    self._translation.get("index"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                col=OrdersViewStyles.ORDER_ITEM_NAME_COL,
                                content=self._get_label(
                                    self._translation.get("name"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                col=OrdersViewStyles.ORDER_ITEM_EAN_COL,
                                content=self._get_label(
                                    self._translation.get("ean"), style=TypographyStyles.SECTION_TITLE, no_wrap=True
                                ),
                            ),
                            ft.Container(
                                col=OrdersViewStyles.ORDER_ITEM_QUANTITY_COL,
                                alignment=ft.Alignment.CENTER_LEFT,
                                content=self._get_label(
                                    self._translation.get("quantity"),
                                    style=TypographyStyles.SECTION_TITLE,
                                    no_wrap=True,
                                ),
                            ),
                            ft.Container(
                                col=OrdersViewStyles.ORDER_ITEM_DISCOUNTS_COL,
                                content=self._get_label(
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
                        content=ft.ResponsiveRow(
                            columns=OrdersViewStyles.ITEMS_ROW_COLUMNS,
                            alignment=OrdersViewStyles.ITEMS_ROW_ALIGNMENT,
                            spacing=OrdersViewStyles.ITEMS_ROW_SPACING,
                            controls=[
                                ft.Container(
                                    col=OrdersViewStyles.ORDER_ITEM_INDEX_COL,
                                    content=self._get_label(
                                        item_index, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS
                                    ),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.ORDER_ITEM_NAME_COL,
                                    content=self._get_label(item_name, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.ORDER_ITEM_EAN_COL,
                                    content=self._get_label(item_ean, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.ORDER_ITEM_QUANTITY_COL,
                                    alignment=ft.Alignment.CENTER_LEFT,
                                    content=self._get_label(quantity, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                                ft.Container(
                                    col=OrdersViewStyles.ORDER_ITEM_DISCOUNTS_COL,
                                    content=self._get_label(discounts, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ),
                            ],
                        ),
                    )
                )
            self._safe_update(self.__items_list)

        self.__status_list.controls.clear()
        if self.__selected_order_id is None:
            self.__status_list.controls.append(self._get_label(self._translation.get("select_order")))
            self._safe_update(self.__status_list)
            return
        if not self.__status_history:
            self.__status_list.controls.append(self._get_label(self._translation.get("no_status_history")))
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
                            self._get_label(status, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            self._get_label(created_at, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                    ),
                )
            )
        self._safe_update(self.__status_list)

    def __handle_download_invoice_clicked(self) -> None:
        self._controller.on_download_invoice_clicked(self.__selected_invoice_id)

    def __build_order_meta_row(
        self,
        label: str,
        value: str,
        trailing_control: ft.Control | None = None,
    ) -> ft.ResponsiveRow:
        if trailing_control is not None:
            value_control: ft.Control = ft.Row(
                spacing=OrdersViewStyles.META_TRAILING_SPACING,
                controls=[
                    self._get_label(str(value), no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                    trailing_control,
                ],
            )
        else:
            value_control = ft.Container(
                expand=True,
                content=self._get_label(str(value), no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
            )
        return ft.ResponsiveRow(
            columns=OrdersViewStyles.META_ROW_COLUMNS,
            controls=[
                ft.Container(
                    col=OrdersViewStyles.ORDER_META_LABEL_COL,
                    content=self._get_label(
                        f"{label}:",
                        style=TypographyStyles.SECTION_TITLE_SEMIBOLD,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ),
                ft.Container(col=OrdersViewStyles.ORDER_META_VALUE_COL, content=value_control),
            ],
            spacing=OrdersViewStyles.META_ROW_SPACING,
        )
