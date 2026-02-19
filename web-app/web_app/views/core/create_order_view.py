from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from schemas.business.trade.order_view_schema import (
    OrderViewCategorySchema,
    OrderViewDiscountSchema,
    OrderViewSourceItemSchema,
)
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles, CreateOrderViewStyles, TypographyStyles
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_view import BaseView
from views.components.cart_dialog_component import CartDialogComponent
from views.components.checkout_dialog_component import CheckoutDialogComponent
from views.components.image_preview_dialog_component import ImagePreviewDialogComponent
from views.components.item_details_dialog_component import ItemDetailsDialogComponent
from views.controls.numeric_field_control import NumericField

if TYPE_CHECKING:
    from controllers.core.create_order_controller import CreateOrderController


class CreateOrderView(BaseView["CreateOrderController"]):
    def __init__(
        self,
        controller: CreateOrderController,
        translation: Translation,
        categories: list[OrderViewCategorySchema],
        items: list[OrderViewSourceItemSchema],
        image_map: dict[int, str | None],
        images_map: dict[int, list[str]],
    ) -> None:
        super().__init__(
            controller=controller,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=View.WEB_CREATE_ORDER,
            data_row=None,
        )
        self.__categories = categories
        self.__items = items
        self.__image_map = image_map
        self.__images_map = images_map
        self.__category_discount_selected: dict[int, str] = {}
        self.__category_discount_dropdowns: dict[int, list[ft.Dropdown]] = {}
        self.__category_discount_items: dict[int, list[int]] = {}
        self.__item_discount_dropdowns: dict[int, ft.Dropdown] = {}
        self.__item_category_dropdowns: dict[int, ft.Dropdown] = {}
        self.__available_nodes: dict[int, ft.Text] = {}
        self.__cart_container: ft.Container | None = None
        self.__cart_dialog: CartDialogComponent | None = None
        self.__cart_list: ft.Column | None = None
        self.__cart_proceed_button: ft.Button | None = None
        self.__cart_has_items: bool = False
        self.__cart_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__cart_previous_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__card: ft.Card | None = None
        self.__card_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__card_previous_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__checkout_dialog: CheckoutDialogComponent | None = None
        self.__checkout_currency_dropdown: ft.Dropdown | None = None
        self.__checkout_customer_discount_dropdown: ft.Dropdown | None = None
        self.__checkout_delivery_method_dropdown: ft.Dropdown | None = None
        self.__checkout_total_net_text: ft.Text | None = None
        self.__checkout_total_gross_text: ft.Text | None = None
        self.__checkout_total_discount_text: ft.Text | None = None
        self.__checkout_shipping_cost_text: ft.Text | None = None
        self.__checkout_total_with_shipping_text: ft.Text | None = None
        self.__checkout_missing_rate_text: ft.Text | None = None
        self.__checkout_confirm_button: ft.Button | None = None
        self.__checkout_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__checkout_previous_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__items_by_id: dict[int, OrderViewSourceItemSchema] = {item.id: item for item in items}
        self.__category_discount_map: dict[int, list[OrderViewDiscountSchema]] = {
            category.id: list(category.discounts) for category in categories
        }
        self.__category_dropdown = self.__build_dropdown(
            key="category_id",
            options=self.__build_category_options(),
            callbacks=[self.__on_category_changed],
            value="0",
        )
        self.__category_dropdown.label = self._translation.get("item_filter")
        self._inputs["category_id"] = self.__wrap_dropdown(self.__category_dropdown)
        self.__items_list = ft.ListView(spacing=AppDimensions.SPACE_SM, expand=True)
        self.__refresh_items_list()

        back_button = ft.TextButton(
            self._translation.get("back_to_orders"),
            on_click=lambda _: self._controller.on_back_to_orders_clicked(),
            style=ButtonStyles.regular,
        )
        header_row = self.__build_responsive_row(
            controls=[
                ft.Container(
                    col=CreateOrderViewStyles.HEADER_BACK_COL,
                    content=back_button,
                    alignment=CreateOrderViewStyles.LEFT_ALIGNMENT,
                ),
                ft.Container(
                    col=CreateOrderViewStyles.HEADER_FILTER_COL,
                    content=self.__category_dropdown,
                    alignment=CreateOrderViewStyles.LEFT_ALIGNMENT,
                ),
            ],
        )
        content_column = ft.Column(
            expand=True,
            spacing=CreateOrderViewStyles.CONTENT_SPACING,
            controls=[
                header_row,
                self.__items_list,
            ],
        )
        self.__card = ft.Card(
            elevation=CreateOrderViewStyles.CARD_ELEVATION,
            bgcolor=CreateOrderViewStyles.CARD_BGCOLOR,
            content=ft.Container(
                content=content_column,
                padding=CreateOrderViewStyles.CARD_PADDING,
                expand=True,
            ),
        )
        self.content = ft.Container(
            expand=True,
            alignment=CreateOrderViewStyles.ROOT_ALIGNMENT,
            content=self.__card,
        )
        self.__apply_card_size()
        self.__register_card_resize_handler()

    def open_cart_dialog(self) -> None:
        self.__cart_list = ft.Column(spacing=AppDimensions.SPACE_XS, tight=True, scroll=ft.ScrollMode.AUTO, expand=True)
        self.__cart_container = ft.Container(content=self.__cart_list)
        self.__cart_dialog = CartDialogComponent(
            translation=self._translation,
            cart_content=self.__cart_container,
            on_continue_clicked=lambda _: self.pop_dialog(),
            on_proceed_clicked=lambda _: self.__on_checkout_clicked(),
        )
        self.__cart_proceed_button = self.__cart_dialog.proceed_button
        self.__ensure_cart_resize_handler()
        self.__render_cart_items()
        self.queue_dialog(self.__cart_dialog)

    def __ensure_cart_resize_handler(self) -> None:
        page = self.app_page
        if self.__cart_resize_handler is not None:
            return
        self.__cart_previous_resize_handler = page.on_resize
        self.__cart_resize_handler = self.__handle_cart_dialog_resize
        page.on_resize = self.__cart_resize_handler

    def __handle_cart_dialog_resize(self, event: ft.ControlEvent) -> None:
        if callable(self.__cart_previous_resize_handler):
            self.__cart_previous_resize_handler(event)
        self.__apply_cart_dialog_size()

    def __resolve_viewport(self) -> tuple[int | None, int | None]:
        return self.get_viewport_size()

    def __apply_cart_dialog_size(self) -> None:
        if not self.__cart_container:
            return
        viewport_width, viewport_height = self.__resolve_viewport()
        if viewport_width:
            target_width = int(viewport_width * CreateOrderViewStyles.CART_DIALOG_WIDTH_RATIO)
            if viewport_width >= CreateOrderViewStyles.CART_DIALOG_BREAKPOINT_DESKTOP:
                target_width = min(target_width, CreateOrderViewStyles.CART_DIALOG_MAX_WIDTH)
            target_width = max(CreateOrderViewStyles.CART_DIALOG_MIN_VIEWPORT_WIDTH, min(target_width, viewport_width))
            target_width = max(
                CreateOrderViewStyles.CART_DIALOG_CONTENT_MIN_WIDTH,
                int(target_width * CreateOrderViewStyles.CART_DIALOG_CONTENT_WIDTH_RATIO),
            )
            self.__cart_container.width = target_width
        else:
            self.__cart_container.width = CreateOrderViewStyles.CART_DIALOG_DEFAULT_WIDTH
        if self.__cart_has_items and viewport_height:
            self.__cart_container.height = int(viewport_height * CreateOrderViewStyles.CART_DIALOG_HEIGHT_RATIO)
        else:
            self.__cart_container.height = None
        self._safe_update(self.__cart_container)

    def __build_responsive_row(
        self,
        controls: Sequence[ft.Control],
        spacing: int | None = None,
        run_spacing: int | None = None,
    ) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            columns=CreateOrderViewStyles.RESPONSIVE_COLUMNS,
            spacing=CreateOrderViewStyles.RESPONSIVE_SPACING if spacing is None else spacing,
            run_spacing=CreateOrderViewStyles.RESPONSIVE_RUN_SPACING if run_spacing is None else run_spacing,
            alignment=CreateOrderViewStyles.RESPONSIVE_ALIGNMENT,
            vertical_alignment=CreateOrderViewStyles.RESPONSIVE_VERTICAL_ALIGNMENT,
            controls=list(controls),
        )

    def __build_single_line_text(
        self,
        value: str,
        align: ft.TextAlign | None = None,
        style: ft.TextStyle | None = None,
    ) -> ft.Text:
        text_kwargs: dict[str, Any] = {
            "no_wrap": True,
            "overflow": ft.TextOverflow.ELLIPSIS,
            "max_lines": 1,
        }
        if align is not None:
            text_kwargs["text_align"] = align
        if style is not None:
            text_kwargs["style"] = style
        return ft.Text(value, **text_kwargs)

    def __build_cart_header_row(self) -> ft.Container:
        return ft.Container(
            padding=CreateOrderViewStyles.CART_HEADER_PADDING,
            content=self.__build_responsive_row(
                controls=[
                    ft.Container(
                        col=CreateOrderViewStyles.CART_ITEM_NAME_COL,
                        content=self.__build_single_line_text(
                            self._translation.get("name"),
                            align=ft.TextAlign.START,
                            style=TypographyStyles.SECTION_TITLE,
                        ),
                    ),
                    ft.Container(
                        col=CreateOrderViewStyles.CART_ITEM_QUANTITY_COL,
                        alignment=CreateOrderViewStyles.LEFT_ALIGNMENT,
                        content=self.__build_single_line_text(
                            self._translation.get("quantity"),
                            align=ft.TextAlign.START,
                            style=TypographyStyles.SECTION_TITLE,
                        ),
                    ),
                    ft.Container(
                        col=CreateOrderViewStyles.CART_ITEM_DISCOUNTS_COL,
                        content=self.__build_single_line_text(
                            self._translation.get("discounts"),
                            align=ft.TextAlign.START,
                            style=TypographyStyles.SECTION_TITLE,
                        ),
                    ),
                    ft.Container(
                        col=CreateOrderViewStyles.CART_ITEM_REMOVE_COL,
                        alignment=CreateOrderViewStyles.CENTER_ALIGNMENT,
                        content=self.__build_single_line_text(
                            self._translation.get("remove"),
                            align=ft.TextAlign.CENTER,
                            style=TypographyStyles.SECTION_TITLE,
                        ),
                    ),
                ]
            ),
        )

    def __build_cart_item_row(self, entry: dict[str, int | float | None]) -> ft.Container | None:
        item_id = entry.get("item_id")
        if not isinstance(item_id, int):
            return None
        item = self.__items_by_id.get(item_id)
        name = item.name if item else str(item_id)
        quantity = int(entry.get("quantity") or 0)
        raw_category_discount_id = entry.get("category_discount_id")
        raw_item_discount_id = entry.get("item_discount_id")
        category_discount_id = raw_category_discount_id if isinstance(raw_category_discount_id, int) else None
        item_discount_id = raw_item_discount_id if isinstance(raw_item_discount_id, int) else None
        category_discounts = self.__category_discount_map.get(item.category_id or -1, []) if item else []
        item_discounts = item.discounts if item else []
        category_label = self.__get_discount_label(category_discount_id, category_discounts)
        item_label = self.__get_discount_label(item_discount_id, item_discounts)
        remove_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip=self._translation.get("remove"),
            on_click=lambda _, selected_item_id=item_id: self.__remove_cart_item(selected_item_id),
            style=ButtonStyles.icon,
        )
        discount_controls: list[ft.Control] = []
        if category_label:
            discount_controls.append(
                self.__build_single_line_text(f"{self._translation.get('category_discount')}: {category_label}")
            )
        if item_label:
            discount_controls.append(
                self.__build_single_line_text(f"{self._translation.get('item_discount')}: {item_label}")
            )
        row_controls: list[ft.Control] = [
            ft.Container(
                col=CreateOrderViewStyles.CART_ITEM_NAME_COL,
                content=self.__build_single_line_text(name, align=ft.TextAlign.START),
            ),
            ft.Container(
                col=CreateOrderViewStyles.CART_ITEM_QUANTITY_COL,
                alignment=CreateOrderViewStyles.LEFT_ALIGNMENT,
                content=self.__build_single_line_text(str(quantity), align=ft.TextAlign.START),
            ),
            ft.Container(
                col=CreateOrderViewStyles.CART_ITEM_DISCOUNTS_COL,
                content=ft.Column(
                    controls=discount_controls,
                    spacing=AppDimensions.SPACE_2XS,
                    tight=True,
                ),
            ),
            ft.Container(
                col=CreateOrderViewStyles.CART_ITEM_REMOVE_COL,
                alignment=CreateOrderViewStyles.CENTER_ALIGNMENT,
                content=remove_button,
            ),
        ]
        return ft.Container(
            padding=CreateOrderViewStyles.CART_ITEM_PADDING,
            border=CreateOrderViewStyles.CART_ITEM_BORDER,
            content=self.__build_responsive_row(controls=row_controls),
        )

    def __render_cart_items(self) -> None:
        if not self.__cart_list or not self.__cart_proceed_button:
            return
        self.__cart_list.controls.clear()
        cart_items = self._controller.get_cart_snapshot()
        if not cart_items:
            self.__cart_has_items = False
            self.__apply_cart_dialog_size()
            self.__cart_list.controls.append(ft.Text(self._translation.get("cart_empty")))
            self.__cart_proceed_button.disabled = True
            self._safe_update(self.__cart_proceed_button)
            self._safe_update(self.__cart_list)
            return
        self.__cart_proceed_button.disabled = False
        self.__cart_has_items = True
        self.__apply_cart_dialog_size()
        self.__cart_list.controls.append(self.__build_cart_header_row())
        for entry in cart_items:
            row = self.__build_cart_item_row(entry)
            if row:
                self.__cart_list.controls.append(row)
        self._safe_update(self.__cart_proceed_button)
        self._safe_update(self.__cart_list)

    def open_checkout_dialog(self) -> None:
        currency_options = self._controller.get_currency_options()
        customer_discount_options = self._controller.get_customer_discount_options()
        delivery_method_options = self._controller.get_delivery_method_options()
        default_currency_id = self._controller.get_default_currency_id()
        self.__checkout_currency_dropdown = self.__build_checkout_dropdown(
            key="currency",
            options=currency_options,
            value=str(default_currency_id) if default_currency_id is not None else "0",
        )
        self.__checkout_customer_discount_dropdown = self.__build_checkout_dropdown(
            key="customer_discount",
            options=customer_discount_options,
            value="0",
        )
        self.__checkout_delivery_method_dropdown = self.__build_checkout_dropdown(
            key="delivery_method",
            options=delivery_method_options,
            value="0",
        )
        if not currency_options and self.__checkout_currency_dropdown:
            self.__checkout_currency_dropdown.disabled = True
            self.__checkout_currency_dropdown.value = "0"
        if not customer_discount_options and self.__checkout_customer_discount_dropdown:
            self.__checkout_customer_discount_dropdown.disabled = True
        if not delivery_method_options and self.__checkout_delivery_method_dropdown:
            self.__checkout_delivery_method_dropdown.disabled = True
        self.__checkout_total_net_text = self.__build_single_line_text("", align=ft.TextAlign.END)
        self.__checkout_total_gross_text = self.__build_single_line_text("", align=ft.TextAlign.END)
        self.__checkout_total_discount_text = self.__build_single_line_text("", align=ft.TextAlign.END)
        self.__checkout_shipping_cost_text = self.__build_single_line_text("", align=ft.TextAlign.END)
        self.__checkout_total_with_shipping_text = self.__build_single_line_text("", align=ft.TextAlign.END)
        self.__checkout_missing_rate_text = ft.Text(
            self._translation.get("missing_exchange_rate"),
            color=CreateOrderViewStyles.CHECKOUT_ERROR_COLOR,
            visible=False,
        )
        self.__checkout_confirm_button = ft.Button(
            content=self._translation.get("confirm_order"),
            disabled=True,
            style=ButtonStyles.primary_regular,
            on_click=lambda _: self.__on_checkout_confirm_clicked(),
        )
        back_button = ft.TextButton(
            self._translation.get("back_to_cart"),
            on_click=lambda _: self.__on_checkout_back_clicked(),
            style=ButtonStyles.regular,
        )
        for dropdown in (
            self.__checkout_currency_dropdown,
            self.__checkout_customer_discount_dropdown,
            self.__checkout_delivery_method_dropdown,
        ):
            if dropdown:
                dropdown.on_select = lambda _: self.__update_checkout_totals()
        totals_rows = self.__build_checkout_totals_rows()
        controls = self.__build_checkout_controls(totals_rows)
        if not self.__checkout_confirm_button:
            return
        self.__checkout_dialog = CheckoutDialogComponent(
            translation=self._translation,
            controls=controls,
            back_button=back_button,
            confirm_button=self.__checkout_confirm_button,
        )
        self.__update_checkout_totals()
        self.__ensure_checkout_resize_handler()
        self.__apply_checkout_dialog_width()
        self.queue_dialog(self.__checkout_dialog)

    def __build_checkout_dropdown(
        self,
        key: str,
        options: list[tuple[int | str, str]],
        value: str,
    ) -> ft.Dropdown:
        dropdown = self.__build_dropdown(key=key, options=options, value=value)
        dropdown.label = self._translation.get(key)
        label = dropdown.label
        if isinstance(label, str):
            dropdown.label = "\n".join(label.split(" "))
        return dropdown

    def __build_checkout_totals_rows(self) -> ft.Column:
        return ft.Column(
            spacing=AppDimensions.SPACE_XS,
            tight=True,
            controls=[
                self.__build_checkout_total_row("total_net", self.__checkout_total_net_text),
                self.__build_checkout_total_row("total_gross", self.__checkout_total_gross_text),
                self.__build_checkout_total_row("total_discount", self.__checkout_total_discount_text),
                self.__build_checkout_total_row("shipping_cost", self.__checkout_shipping_cost_text),
                self.__build_checkout_total_row("total_with_shipping", self.__checkout_total_with_shipping_text),
            ],
        )

    def __build_checkout_total_row(self, label_key: str, value_control: ft.Control | None) -> ft.ResponsiveRow:
        return self.__build_responsive_row(
            controls=[
                ft.Container(
                    col=CreateOrderViewStyles.CHECKOUT_TOTAL_LABEL_COL,
                    content=self.__build_single_line_text(self._translation.get(label_key)),
                ),
                ft.Container(
                    col=CreateOrderViewStyles.CHECKOUT_TOTAL_VALUE_COL,
                    alignment=CreateOrderViewStyles.RIGHT_ALIGNMENT,
                    content=value_control,
                ),
            ],
            spacing=CreateOrderViewStyles.CHECKOUT_TOTAL_ROW_SPACING,
            run_spacing=CreateOrderViewStyles.CHECKOUT_TOTAL_ROW_RUN_SPACING,
        )

    def __build_checkout_controls(self, totals_rows: ft.Column) -> list[ft.Control]:
        controls: list[ft.Control] = [
            self.__build_responsive_row(
                controls=[
                    ft.Container(
                        col=CreateOrderViewStyles.CHECKOUT_FILTER_COL,
                        content=self.__checkout_currency_dropdown,
                        expand=True,
                    ),
                    ft.Container(
                        col=CreateOrderViewStyles.CHECKOUT_FILTER_COL,
                        content=self.__checkout_customer_discount_dropdown,
                        expand=True,
                    ),
                    ft.Container(
                        col=CreateOrderViewStyles.CHECKOUT_FILTER_COL,
                        content=self.__checkout_delivery_method_dropdown,
                        expand=True,
                    ),
                ]
            ),
            ft.Container(
                content=self.__checkout_missing_rate_text, padding=CreateOrderViewStyles.CHECKOUT_MISSING_RATE_PADDING
            ),
            ft.Container(height=AppDimensions.SPACE_SM),
            totals_rows,
        ]
        return controls

    def __update_checkout_totals(self) -> None:
        if (
            self.__checkout_currency_dropdown is None
            or self.__checkout_customer_discount_dropdown is None
            or self.__checkout_delivery_method_dropdown is None
            or self.__checkout_total_net_text is None
            or self.__checkout_total_gross_text is None
            or self.__checkout_total_discount_text is None
            or self.__checkout_shipping_cost_text is None
            or self.__checkout_total_with_shipping_text is None
            or self.__checkout_missing_rate_text is None
            or self.__checkout_confirm_button is None
        ):
            return
        currency_id = self.__parse_optional_int(self.__checkout_currency_dropdown.value)
        customer_discount_id = self.__parse_optional_int(self.__checkout_customer_discount_dropdown.value)
        delivery_method_id = self.__parse_optional_int(self.__checkout_delivery_method_dropdown.value)
        (
            total_net,
            _,
            total_gross,
            total_discount,
            shipping_cost,
            total_with_shipping,
            label,
            has_missing_rate,
        ) = self._controller.compute_checkout_summary(currency_id, customer_discount_id, delivery_method_id)
        self.__checkout_missing_rate_text.visible = has_missing_rate
        self.__checkout_confirm_button.disabled = (
            has_missing_rate or currency_id is None or not self._controller.get_cart_snapshot()
        )
        if not has_missing_rate:
            self.__checkout_total_net_text.value = self.__format_checkout_amount(total_net, label)
            self.__checkout_total_gross_text.value = self.__format_checkout_amount(total_gross, label)
            self.__checkout_total_discount_text.value = self.__format_checkout_amount(total_discount, label)
            self.__checkout_shipping_cost_text.value = self.__format_checkout_amount(shipping_cost, label)
            self.__checkout_total_with_shipping_text.value = self.__format_checkout_amount(total_with_shipping, label)
            self._safe_update(self.__checkout_total_net_text)
            self._safe_update(self.__checkout_total_gross_text)
            self._safe_update(self.__checkout_total_discount_text)
            self._safe_update(self.__checkout_shipping_cost_text)
            self._safe_update(self.__checkout_total_with_shipping_text)
        self._safe_update(self.__checkout_missing_rate_text)
        self._safe_update(self.__checkout_confirm_button)

    @staticmethod
    def __format_checkout_amount(amount: float, label: str) -> str:
        if label:
            return f"{amount:.2f} {label}"
        return f"{amount:.2f}"

    def __ensure_checkout_resize_handler(self) -> None:
        page = self.app_page
        if self.__checkout_resize_handler is not None:
            return
        self.__checkout_previous_resize_handler = page.on_resize
        self.__checkout_resize_handler = self.__handle_checkout_dialog_resize
        page.on_resize = self.__checkout_resize_handler

    def __handle_checkout_dialog_resize(self, event: ft.ControlEvent) -> None:
        if callable(self.__checkout_previous_resize_handler):
            self.__checkout_previous_resize_handler(event)
        self.__apply_checkout_dialog_width()

    def __resolve_checkout_dialog_width(self) -> int:
        page = self.app_page
        viewport_width = page.width or page.window.width
        if viewport_width:
            return max(
                CreateOrderViewStyles.CHECKOUT_DIALOG_MIN_WIDTH,
                min(
                    int(viewport_width * CreateOrderViewStyles.CHECKOUT_DIALOG_WIDTH_RATIO),
                    CreateOrderViewStyles.CHECKOUT_DIALOG_MAX_WIDTH,
                ),
            )
        return CreateOrderViewStyles.CHECKOUT_DIALOG_DEFAULT_WIDTH

    def __apply_checkout_dialog_width(self) -> None:
        if not self.__checkout_dialog:
            return
        self.__checkout_dialog.set_content_width(self.__resolve_checkout_dialog_width())
        self._safe_update(self.__checkout_dialog)

    def refresh_items_list(self) -> None:
        self.__refresh_items_list()

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

    def __build_category_options(self) -> list[tuple[int | str, str]]:
        options: list[tuple[int | str, str]] = [(category.id, category.label) for category in self.__categories]
        return options

    def __build_discount_options(self, discounts: list[OrderViewDiscountSchema]) -> list[tuple[int | str, str]]:
        return [(discount.id, f"{discount.code} ({(discount.percent or 0) * 100:.0f}%)") for discount in discounts]

    def __build_dropdown(
        self,
        key: str,
        options: list[tuple[int | str, str]],
        value: str | None = "",
        callbacks: list[Any] | None = None,
    ) -> ft.Dropdown:
        def handle_select(_: ft.Event[ft.Dropdown]) -> None:
            for callback in callbacks or []:
                callback()

        dropdown = self._get_dropdown(
            key=key,
            options=options,
            value=value if value is not None else "0",
            on_select=handle_select,
        )
        return dropdown

    def __build_numeric_input(
        self,
        key: str,
        value: int | float,
        step: int | float,
        precision: int,
        min_value: int | float | None,
        max_value: int | float | None,
        is_float: bool,
        read_only: bool,
        on_change: Callable[[ft.ControlEvent], None],
    ) -> tuple[ft.Container, NumericField]:
        numeric_field = self._get_numeric_field(
            value=value,
            step=step,
            precision=precision,
            min_value=min_value,
            max_value=max_value,
            is_float=is_float,
            read_only=read_only,
            on_change=on_change,
            expand=True,
        )
        container = ft.Container(key=key, content=numeric_field, expand=True)
        return container, numeric_field

    def __build_item_row(
        self, item: OrderViewSourceItemSchema, cart_quantities: dict[int, int] | None = None
    ) -> ft.Control:
        if cart_quantities is None:
            cart_quantities = self.__normalize_cart_quantities(self._controller.get_cart_quantities())
        else:
            cart_quantities = self.__normalize_cart_quantities(cart_quantities)
        image_url = self.__image_map.get(item.id)
        image = ft.Container(
            width=AppDimensions.CREATE_ORDER_IMAGE_BOX_SIZE,
            height=AppDimensions.CREATE_ORDER_IMAGE_BOX_SIZE,
            alignment=ft.Alignment.CENTER,
            border=CreateOrderViewStyles.ITEM_IMAGE_BORDER,
            content=(
                ft.Image(
                    src=image_url,
                    width=AppDimensions.CREATE_ORDER_IMAGE_SIZE,
                    height=AppDimensions.CREATE_ORDER_IMAGE_SIZE,
                    fit=ft.BoxFit.CONTAIN,
                )
                if image_url
                else None
            ),
            on_click=lambda _: self.__open_item_dialog(item),
        )
        available = self.__get_available_quantity(item, cart_quantities)
        available_text = ft.Text(f"{self._translation.get('available')}: {available}")
        self.__available_nodes[item.id] = available_text
        details = ft.Column(
            spacing=CreateOrderViewStyles.DETAILS_COLUMN_SPACING,
            controls=[
                ft.Text(item.name, style=TypographyStyles.SECTION_TITLE),
                ft.Text(f"{self._translation.get('index')}: {item.index}"),
                available_text,
                ft.Text(f"{self._translation.get('moq')}: {item.moq}"),
            ],
            expand=True,
        )
        details_container = ft.Container(content=details, expand=True, on_click=lambda _: self.__open_item_dialog(item))
        category_discount_dropdown = self.__build_dropdown(
            key=f"category_discount_{item.id}",
            options=self.__build_discount_options(self.__get_category_discounts(item.category_id)),
            value="0",
        )
        category_discount_dropdown.label = self._translation.get("category_discount")
        item_discount_dropdown = self.__build_dropdown(
            key=f"item_discount_{item.id}",
            options=self.__build_discount_options(item.discounts),
            value="0",
        )
        item_discount_dropdown.label = self._translation.get("item_discount")
        self._inputs[f"category_discount_{item.id}"] = self.__wrap_dropdown(category_discount_dropdown)
        self._inputs[f"item_discount_{item.id}"] = self.__wrap_dropdown(item_discount_dropdown)
        self.__item_category_dropdowns[item.id] = category_discount_dropdown
        self.__item_discount_dropdowns[item.id] = item_discount_dropdown
        if item.category_id is not None:
            self.__category_discount_dropdowns.setdefault(item.category_id, []).append(category_discount_dropdown)
            self.__category_discount_items.setdefault(item.category_id, []).append(item.id)
            selected = self.__category_discount_selected.get(item.category_id)
            if selected:
                category_discount_dropdown.value = selected

        qty_input_container, qty_input = self.__build_numeric_input(
            key=f"quantity_{item.id}",
            value=0,
            step=item.moq,
            precision=0,
            min_value=0,
            max_value=None,
            is_float=False,
            read_only=False,
            on_change=lambda event: self.__handle_quantity_change(event, item),
        )
        qty_input_container.expand = True
        category_discount_dropdown.on_select = lambda _: self.__on_item_category_discount_changed(
            item,
            category_discount_dropdown,
            lambda: None,
        )
        item_discount_dropdown.on_select = lambda _: self.__on_item_discount_changed(
            item,
            item_discount_dropdown,
            lambda: None,
        )
        add_button = ft.Button(
            content=self._translation.get("add_to_cart"),
            disabled=True,
            style=ButtonStyles.add_to_cart,
            on_click=lambda _: self.__on_add_to_cart_clicked(
                item,
                qty_input,
                category_discount_dropdown,
                item_discount_dropdown,
            ),
        )
        return ft.Container(
            padding=CreateOrderViewStyles.ITEM_ROW_PADDING,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=AppDimensions.SPACE_LG,
                expand=True,
                controls=[
                    image,
                    details_container,
                    ft.Container(content=category_discount_dropdown, expand=True),
                    ft.Container(content=item_discount_dropdown, expand=True),
                    qty_input_container,
                    ft.Container(content=add_button, expand=True),
                ],
            ),
            expand=True,
        )

    def __filter_items_by_category(self, items: list[OrderViewSourceItemSchema]) -> list[OrderViewSourceItemSchema]:
        selected = self.__category_dropdown.value
        if not selected or selected in {"0", "all"}:
            return list(items)
        try:
            category_id = int(selected)
        except ValueError:
            return list(items)
        return [item for item in items if item.category_id == category_id]

    def __get_category_discounts(self, category_id: int | None) -> list[OrderViewDiscountSchema]:
        if category_id is None:
            return []
        category = next((item for item in self.__categories if item.id == category_id), None)
        return list(category.discounts) if category else []

    def __handle_quantity_change(self, event: ft.ControlEvent, item: OrderViewSourceItemSchema) -> None:
        control = event.control
        if not isinstance(control, NumericField):
            return
        value = control.value
        if value is None or value == 0:
            control.error = None
            self.__toggle_add_button(control, False)
            return
        if int(value) % item.moq != 0:
            control.error = self._translation.get("invalid_quantity")
            self.__toggle_add_button(control, False)
            return
        available = self.__get_available_quantity(
            item, self.__normalize_cart_quantities(self._controller.get_cart_quantities())
        )
        if int(value) > available:
            control.error = self._translation.get("insufficient_stock")
            self.__toggle_add_button(control, False)
            return
        control.error = None
        self.__toggle_add_button(control, True)

    def __on_add_to_cart_clicked(
        self,
        item: OrderViewSourceItemSchema,
        qty_input: NumericField,
        category_dropdown: ft.Dropdown,
        item_dropdown: ft.Dropdown,
    ) -> None:
        quantity = qty_input.value
        if quantity is None or quantity == 0 or int(quantity) % item.moq != 0:
            qty_input.error = self._translation.get("invalid_quantity")
            return
        available = self.__get_available_quantity(item, self._controller.get_cart_quantities())
        if int(quantity) > available:
            qty_input.error = self._translation.get("insufficient_stock")
            return
        qty_input.error = None
        category_discount_id = self.__parse_optional_int(category_dropdown.value)
        item_discount_id = self.__parse_optional_int(item_dropdown.value)
        self._controller.on_add_to_cart(
            item.id,
            int(quantity),
            item.category_id,
            category_discount_id,
            item_discount_id,
        )
        qty_input.value = 0
        qty_input.error = None
        self._safe_update(qty_input)
        self.__toggle_add_button(qty_input, False)
        self.__update_available_for_item(item.id)

    def __on_category_changed(self) -> None:
        self.__refresh_items_list()

    def __on_checkout_back_clicked(self) -> None:
        self.pop_dialog()
        self.open_cart_dialog()

    def __on_checkout_clicked(self) -> None:
        self.pop_dialog()
        self._controller.on_checkout_requested()

    def __on_checkout_confirm_clicked(
        self,
    ) -> None:
        if (
            self.__checkout_currency_dropdown is None
            or self.__checkout_customer_discount_dropdown is None
            or self.__checkout_delivery_method_dropdown is None
        ):
            return
        currency_id = self.__parse_optional_int(self.__checkout_currency_dropdown.value)
        if currency_id is None:
            return
        customer_discount_id = self.__parse_optional_int(self.__checkout_customer_discount_dropdown.value)
        delivery_method_id = self.__parse_optional_int(self.__checkout_delivery_method_dropdown.value)
        self.pop_dialog()
        self._controller.on_checkout_confirm(currency_id, customer_discount_id, delivery_method_id)

    def __on_item_category_discount_changed(
        self,
        item: OrderViewSourceItemSchema,
        category_dropdown: ft.Dropdown,
        update_prices: Any,
    ) -> None:
        if item.category_id is None:
            update_prices()
            return
        selected_value = category_dropdown.value or "0"
        self.__category_discount_selected[item.category_id] = selected_value
        for dropdown in self.__category_discount_dropdowns.get(item.category_id, []):
            if dropdown is category_dropdown:
                continue
            dropdown.value = selected_value
            self._safe_update(dropdown)
        self._controller.on_category_discount_changed(item.category_id, selected_value)
        update_prices()

    def __on_item_discount_changed(
        self,
        item: OrderViewSourceItemSchema,
        item_dropdown: ft.Dropdown,
        update_prices: Any,
    ) -> None:
        selected_value = item_dropdown.value or "0"
        self._controller.on_item_discount_changed(item.id, selected_value)
        update_prices()

    def __open_image_dialog(self, url: str) -> None:
        dialog = ImagePreviewDialogComponent(
            translation=self._translation,
            image_url=url,
            on_ok_clicked=lambda _: self.pop_dialog(),
        )
        self.queue_dialog(dialog)

    def __open_item_dialog(self, item: OrderViewSourceItemSchema) -> None:
        available_quantity = max(0, item.stock_quantity - item.reserved_quantity)
        description = item.description
        is_fragile = item.is_fragile
        expiration_date = item.expiration_date
        category_name = item.category_name
        fragile_value = ""
        if is_fragile is True:
            fragile_value = self._translation.get("yes")
        elif is_fragile is False:
            fragile_value = self._translation.get("no")
        detail_rows: list[tuple[str, str]] = [
            ("name", item.name),
            ("index", item.index),
            ("ean", item.ean),
            ("description", description or ""),
            ("is_fragile", fragile_value),
            ("expiration_date", "" if expiration_date is None else str(expiration_date)),
            ("category_name", category_name or ""),
            ("available", str(available_quantity)),
            ("vat_rate", str(item.vat_rate)),
            ("moq", str(item.moq)),
            ("dimensions", f"{item.width}x{item.height}x{item.length}"),
            ("weight", str(item.weight)),
        ]
        image_urls = self.__images_map.get(item.id, [])
        dialog = ItemDetailsDialogComponent(
            translation=self._translation,
            detail_rows=detail_rows,
            image_urls=image_urls,
            on_image_clicked=self.__open_image_dialog,
            on_ok_clicked=lambda _: self.pop_dialog(),
            safe_update=self._safe_update,
        )
        self.queue_dialog(dialog)

    def __refresh_items_list(self) -> None:
        filtered_items = self.__filter_items_by_category(self.__items)
        cart_quantities = self.__normalize_cart_quantities(self._controller.get_cart_quantities())
        self.__available_nodes.clear()
        self.__items_list.controls = [self.__build_item_row(item, cart_quantities) for item in filtered_items]
        self._safe_update(self.__items_list)

    def __register_card_resize_handler(self) -> None:
        page = self.app_page
        if self.__card_resize_handler is not None:
            return
        self.__card_previous_resize_handler = getattr(page, "on_resize", None)
        self.__card_resize_handler = self.__handle_card_resize
        setattr(page, "on_resize", self.__card_resize_handler)

    def __handle_card_resize(self, event: ft.ControlEvent) -> None:
        if callable(self.__card_previous_resize_handler):
            self.__card_previous_resize_handler(event)
        self.__apply_card_size()

    def __remove_cart_item(self, item_id: int) -> None:
        self._controller.remove_from_cart(item_id)
        self.__update_available_for_item(item_id)
        self.__render_cart_items()

    def __get_available_quantity(self, item: OrderViewSourceItemSchema, cart_quantities: dict[int, int]) -> int:
        base_available = max(0, item.stock_quantity - item.reserved_quantity)
        cart_quantity = cart_quantities.get(item.id, 0)
        return max(0, base_available - cart_quantity)

    def __get_discount_label(self, discount_id: int | None, discounts: list[OrderViewDiscountSchema]) -> str | None:
        if discount_id is None:
            return None
        for discount in discounts:
            if discount.id == discount_id:
                percent = (discount.percent or 0) * 100
                return f"{discount.code} ({percent:.0f}%)"
        return None

    def __toggle_add_button(self, qty_input: NumericField, enabled: bool) -> None:
        parent = qty_input.parent
        if not isinstance(parent, ft.Container):
            return
        row = parent.parent
        if not isinstance(row, ft.Row):
            return
        for control in row.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Button):
                control.content.disabled = not enabled
                self._safe_update(control.content)
                break

    def __update_available_for_item(self, item_id: int) -> None:
        item = self.__items_by_id.get(item_id)
        if not item:
            return
        node = self.__available_nodes.get(item_id)
        if not node:
            return
        available = self.__get_available_quantity(
            item, self.__normalize_cart_quantities(self._controller.get_cart_quantities())
        )
        node.value = f"{self._translation.get('available')}: {available}"
        self._safe_update(node)

    @staticmethod
    def __normalize_cart_quantities(cart_quantities: Any) -> dict[int, int]:
        if not isinstance(cart_quantities, dict):
            return {}
        normalized: dict[int, int] = {}
        for raw_key, raw_value in cart_quantities.items():
            try:
                key = int(raw_key)
                value = int(raw_value)
            except (TypeError, ValueError):
                continue
            normalized[key] = value
        return normalized

    @staticmethod
    def __parse_optional_int(value: str | None) -> int | None:
        if not value or value in {"0", ""}:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def __wrap_dropdown(self, dropdown: ft.Dropdown) -> FieldGroup:
        return FieldGroup(
            label=(ft.Container(), 0),
            input=(ft.Container(content=dropdown), 0),
            marker=(ft.Container(), 0),
        )
