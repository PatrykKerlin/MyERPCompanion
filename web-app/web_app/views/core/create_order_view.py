from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from schemas.business.trade.order_view_schema import (
    OrderViewCategorySchema,
    OrderViewDiscountSchema,
    OrderViewSourceItemSchema,
)
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView
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
            base_label_size=0,
            base_input_size=0,
            base_columns_qty=12,
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
        self.__cart_has_items: bool = False
        self.__cart_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__card: ft.Card | None = None
        self.__card_resize_handler: Callable[[ft.ControlEvent], None] | None = None
        self.__items_by_id: dict[int, OrderViewSourceItemSchema] = {item.id: item for item in items}
        self.__category_discount_map: dict[int, list[OrderViewDiscountSchema]] = {
            category.id: list(category.discounts) for category in categories
        }
        _category_dropdown_container, self.__category_dropdown = self.__build_dropdown(
            key="category_id",
            options=self.__build_category_options(),
            callbacks=[self.__on_category_changed],
            value="0",
        )
        self.__category_dropdown.label = self._translation.get("item_filter")
        self._inputs["category_id"] = self.__wrap_dropdown(self.__category_dropdown)
        self.__items_list = ft.ListView(spacing=8, expand=True)
        self.__refresh_items_list()

        back_button = ft.TextButton(
            self._translation.get("back_to_orders"),
            on_click=lambda _: self._controller.on_back_to_orders_clicked(),
        )
        header_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 2},
                    content=back_button,
                    alignment=ft.Alignment.CENTER_LEFT,
                ),
                ft.Container(
                    col={"sm": 12, "md": 10},
                    content=self.__category_dropdown,
                    alignment=ft.Alignment.CENTER_LEFT,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        content_column = ft.Column(
            expand=True,
            controls=[
                header_row,
                ft.Container(height=8),
                self.__items_list,
            ],
        )
        self.__card = ft.Card(
            elevation=2,
            content=ft.Container(
                content=content_column,
                padding=ft.Padding.all(16),
                expand=True,
            ),
        )
        self.content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=self.__card,
        )
        self.__apply_card_size()
        self.__register_card_resize_handler()

    def open_cart_dialog(self) -> None:
        cart_list = ft.Column(spacing=6, tight=True, scroll=ft.ScrollMode.AUTO, expand=True)
        proceed_button = ft.Button(
            content=self._translation.get("proceed_to_checkout"),
            on_click=lambda _: self.__on_checkout_clicked(),
        )
        continue_button = ft.TextButton(
            self._translation.get("continue_shopping"),
            on_click=lambda _: self._controller._page.pop_dialog(),
        )
        page = self._controller._page
        cart_container = ft.Container(content=cart_list)
        self.__cart_container = cart_container

        def resolve_viewport() -> tuple[int | None, int | None]:
            return (page.width or page.window.width, page.height or page.window.height)

        def apply_size() -> None:
            if not self.__cart_container:
                return
            viewport_width, viewport_height = resolve_viewport()
            if viewport_width:
                target_width = int(viewport_width * 0.95)
                if viewport_width >= 900:
                    target_width = min(target_width, 960)
                target_width = max(320, min(target_width, viewport_width))
                target_width = max(380, int(target_width * 0.72))
                self.__cart_container.width = target_width
            else:
                self.__cart_container.width = 460
            if self.__cart_has_items and viewport_height:
                self.__cart_container.height = int(viewport_height * 0.5)
            else:
                self.__cart_container.height = None
            self.__safe_update(self.__cart_container)

        if self.__cart_resize_handler is None:
            previous_handler = page.on_resize

            def handle_resize(event: ft.ControlEvent) -> None:
                if callable(previous_handler):
                    previous_handler(event)
                apply_size()

            self.__cart_resize_handler = handle_resize
            page.on_resize = handle_resize

        def build_text(value: str, align: ft.TextAlign | None = None, weight: ft.FontWeight | None = None) -> ft.Text:
            return ft.Text(
                value,
                no_wrap=True,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
                text_align=align,
                weight=weight,
            )

        def render_cart_items() -> None:
            cart_list.controls.clear()
            cart_items = self._controller.get_cart_snapshot()
            if not cart_items:
                self.__cart_has_items = False
                apply_size()
                cart_list.controls.append(ft.Text(self._translation.get("cart_empty")))
                proceed_button.disabled = True
                self.__safe_update(proceed_button)
                self.__safe_update(cart_list)
                return

            proceed_button.disabled = False
            self.__cart_has_items = True
            apply_size()
            cart_list.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                    content=ft.ResponsiveRow(
                        columns=12,
                        spacing=4,
                        run_spacing=4,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                col={"sm": 12, "md": 3},
                                content=build_text(
                                    self._translation.get("name"),
                                    align=ft.TextAlign.START,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 6, "md": 3},
                                alignment=ft.Alignment.CENTER_LEFT,
                                content=build_text(
                                    self._translation.get("quantity"),
                                    align=ft.TextAlign.START,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 5},
                                content=build_text(
                                    self._translation.get("discounts"),
                                    align=ft.TextAlign.START,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 6, "md": 1},
                                alignment=ft.Alignment.CENTER,
                                content=build_text(
                                    self._translation.get("remove"),
                                    align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),
                )
            )
            for entry in cart_items:
                item_id = entry.get("item_id")
                if not isinstance(item_id, int):
                    continue
                item = self.__items_by_id.get(item_id)
                name = item.name if item else str(item_id)
                quantity = int(entry.get("quantity") or 0)
                category_discount_id = entry.get("category_discount_id")
                item_discount_id = entry.get("item_discount_id")
                category_discounts = self.__category_discount_map.get(item.category_id or -1, []) if item else []
                item_discounts = item.discounts if item else []
                category_label = self.__resolve_discount_label(category_discount_id, category_discounts)
                item_label = self.__resolve_discount_label(item_discount_id, item_discounts)

                remove_button = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    tooltip=self._translation.get("remove"),
                    on_click=lambda _, i=item_id: self.__remove_cart_item(i, render_cart_items),
                )
                discount_controls: list[ft.Control] = []
                if category_label:
                    discount_controls.append(
                        build_text(f"{self._translation.get('category_discount')}: {category_label}")
                    )
                if item_label:
                    discount_controls.append(build_text(f"{self._translation.get('item_discount')}: {item_label}"))
                row_controls: list[ft.Control] = [
                    ft.Container(
                        col={"sm": 12, "md": 3},
                        content=build_text(name, align=ft.TextAlign.START),
                    ),
                    ft.Container(
                        col={"sm": 6, "md": 3},
                        alignment=ft.Alignment.CENTER_LEFT,
                        content=build_text(str(quantity), align=ft.TextAlign.START),
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        content=ft.Column(
                            controls=discount_controls,
                            spacing=2,
                            tight=True,
                        ),
                    ),
                    ft.Container(
                        col={"sm": 6, "md": 1},
                        alignment=ft.Alignment.CENTER,
                        content=remove_button,
                    ),
                ]
                cart_list.controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=6, horizontal=6),
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        content=ft.ResponsiveRow(
                            columns=12,
                            spacing=4,
                            run_spacing=4,
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=row_controls,
                        ),
                    )
                )
            self.__safe_update(proceed_button)
            self.__safe_update(cart_list)

        render_cart_items()
        dialog = BaseDialog(
            title=self._translation.get("cart"),
            controls=[cart_container],
            actions=[continue_button, proceed_button],
        )
        self._controller._queue_dialog(dialog)

    def open_checkout_dialog(self) -> None:
        currency_options = self._controller.get_currency_options()
        customer_discount_options = self._controller.get_customer_discount_options()
        delivery_method_options = self._controller.get_delivery_method_options()
        default_currency_id = self._controller.get_default_currency_id()

        def build_text(value: str, align: ft.TextAlign | None = None) -> ft.Text:
            return ft.Text(
                value,
                no_wrap=True,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
                text_align=align,
            )

        currency_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key="0", text="")]
            + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in currency_options],
            value=str(default_currency_id) if default_currency_id is not None else "0",
            label=self._translation.get("currency"),
            expand=True,
            editable=True,
            enable_search=True,
            enable_filter=True,
        )
        if not currency_options:
            currency_dropdown.disabled = True
            currency_dropdown.value = "0"
        if currency_dropdown.label:
            currency_dropdown.label = "\n".join(currency_dropdown.label.split(" "))

        customer_discount_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key="0", text="")]
            + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in customer_discount_options],
            value="0",
            label=self._translation.get("customer_discount"),
            expand=True,
            editable=True,
            enable_search=True,
            enable_filter=True,
        )
        if not customer_discount_options:
            customer_discount_dropdown.disabled = True
        if customer_discount_dropdown.label:
            customer_discount_dropdown.label = "\n".join(customer_discount_dropdown.label.split(" "))

        delivery_method_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key="0", text="")]
            + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in delivery_method_options],
            value="0",
            label=self._translation.get("delivery_method"),
            expand=True,
            editable=True,
            enable_search=True,
            enable_filter=True,
        )
        if not delivery_method_options:
            delivery_method_dropdown.disabled = True
        if delivery_method_dropdown.label:
            delivery_method_dropdown.label = "\n".join(delivery_method_dropdown.label.split(" "))

        total_net_text = build_text("", align=ft.TextAlign.END)
        total_gross_text = build_text("", align=ft.TextAlign.END)
        total_discount_text = build_text("", align=ft.TextAlign.END)
        shipping_cost_text = build_text("", align=ft.TextAlign.END)
        total_with_shipping_text = build_text("", align=ft.TextAlign.END)
        missing_rate_text = ft.Text(
            self._translation.get("missing_exchange_rate"),
            color=ft.Colors.ERROR,
            visible=False,
        )
        confirm_button = ft.Button(
            content=self._translation.get("confirm_order"),
            disabled=True,
        )
        back_button = ft.TextButton(
            self._translation.get("back_to_cart"),
            on_click=lambda _: self.__on_checkout_back_clicked(),
        )

        def parse_dropdown_int(value: str | None) -> int | None:
            if not value or value in {"0", ""}:
                return None
            try:
                return int(value)
            except ValueError:
                return None

        def format_amount(amount: float, label: str) -> str:
            if label:
                return f"{amount:.2f} {label}"
            return f"{amount:.2f}"

        def update_totals() -> None:
            currency_id = parse_dropdown_int(currency_dropdown.value)
            customer_discount_id = parse_dropdown_int(customer_discount_dropdown.value)
            delivery_method_id = parse_dropdown_int(delivery_method_dropdown.value)
            (
                total_net,
                _total_vat,
                total_gross,
                total_discount,
                shipping_cost,
                total_with_shipping,
                label,
                has_missing_rate,
            ) = self._controller.compute_checkout_summary(currency_id, customer_discount_id, delivery_method_id)
            missing_rate_text.visible = has_missing_rate
            confirm_button.disabled = (
                has_missing_rate or currency_id is None or not self._controller.get_cart_snapshot()
            )
            if not has_missing_rate:
                total_net_text.value = format_amount(total_net, label)
                total_gross_text.value = format_amount(total_gross, label)
                total_discount_text.value = format_amount(total_discount, label)
                shipping_cost_text.value = format_amount(shipping_cost, label)
                total_with_shipping_text.value = format_amount(total_with_shipping, label)
                self.__safe_update(total_net_text)
                self.__safe_update(total_gross_text)
                self.__safe_update(total_discount_text)
                self.__safe_update(shipping_cost_text)
                self.__safe_update(total_with_shipping_text)
            self.__safe_update(missing_rate_text)
            self.__safe_update(confirm_button)

        currency_dropdown.on_change = lambda _: update_totals()
        currency_dropdown.on_select = lambda _: update_totals()
        customer_discount_dropdown.on_change = lambda _: update_totals()
        customer_discount_dropdown.on_select = lambda _: update_totals()
        delivery_method_dropdown.on_change = lambda _: update_totals()
        delivery_method_dropdown.on_select = lambda _: update_totals()

        confirm_button.on_click = lambda _: self.__on_checkout_confirm_clicked(
            currency_dropdown,
            customer_discount_dropdown,
            delivery_method_dropdown,
        )

        totals_rows = ft.Column(
            spacing=6,
            tight=True,
            controls=[
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(col={"sm": 6, "md": 4}, content=build_text(self._translation.get("total_net"))),
                        ft.Container(
                            col={"sm": 6, "md": 8},
                            alignment=ft.Alignment.CENTER_RIGHT,
                            content=total_net_text,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(col={"sm": 6, "md": 4}, content=build_text(self._translation.get("total_gross"))),
                        ft.Container(
                            col={"sm": 6, "md": 8},
                            alignment=ft.Alignment.CENTER_RIGHT,
                            content=total_gross_text,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(
                            col={"sm": 6, "md": 4}, content=build_text(self._translation.get("total_discount"))
                        ),
                        ft.Container(
                            col={"sm": 6, "md": 8},
                            alignment=ft.Alignment.CENTER_RIGHT,
                            content=total_discount_text,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(
                            col={"sm": 6, "md": 4}, content=build_text(self._translation.get("shipping_cost"))
                        ),
                        ft.Container(
                            col={"sm": 6, "md": 8},
                            alignment=ft.Alignment.CENTER_RIGHT,
                            content=shipping_cost_text,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(
                            col={"sm": 6, "md": 4}, content=build_text(self._translation.get("total_with_shipping"))
                        ),
                        ft.Container(
                            col={"sm": 6, "md": 8},
                            alignment=ft.Alignment.CENTER_RIGHT,
                            content=total_with_shipping_text,
                        ),
                    ],
                ),
            ],
        )

        controls: list[ft.Control] = [
            ft.ResponsiveRow(
                columns=12,
                controls=[
                    ft.Container(col={"sm": 12, "md": 4}, content=currency_dropdown, expand=True),
                    ft.Container(col={"sm": 12, "md": 4}, content=customer_discount_dropdown, expand=True),
                    ft.Container(col={"sm": 12, "md": 4}, content=delivery_method_dropdown, expand=True),
                ],
            ),
            ft.Container(content=missing_rate_text, padding=ft.Padding.only(top=4)),
            ft.Container(height=8),
            totals_rows,
        ]

        update_totals()
        dialog = BaseDialog(
            title=self._translation.get("checkout"),
            controls=controls,
            actions=[back_button, confirm_button],
        )
        if isinstance(dialog.content, ft.Container) and isinstance(dialog.content.content, ft.Column):
            dialog.content.content.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        page = self._controller._page

        def resolve_width() -> int:
            viewport_width = page.width or page.window.width
            if viewport_width:
                return max(360, min(int(viewport_width * 0.9), 720))
            return 600

        def apply_width() -> None:
            target_width = resolve_width()
            dialog.width = target_width
            dialog.content.width = target_width
            self.__safe_update(dialog)

        apply_width()
        previous_handler = page.on_resize

        def handle_resize(event: ft.ControlEvent) -> None:
            if callable(previous_handler):
                previous_handler(event)
            apply_width()

        page.on_resize = handle_resize
        self._controller._queue_dialog(dialog)

    def refresh_items_list(self) -> None:
        self.__refresh_items_list()

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
    ) -> tuple[ft.Container, ft.Dropdown]:
        container, _ = self._get_dropdown(key=key, size=6, options=options, callbacks=callbacks)
        dropdown = container.content
        if not isinstance(dropdown, ft.Dropdown):
            raise TypeError("Expected Dropdown content.")
        if value is not None:
            dropdown.value = value
        return container, dropdown

    def __build_item_row(
        self, item: OrderViewSourceItemSchema, cart_quantities: dict[int, int] | None = None
    ) -> ft.Control:
        if cart_quantities is None:
            cart_quantities = self._controller.get_cart_quantities()
        image_url = self.__image_map.get(item.id)
        image = ft.Container(
            width=64,
            height=64,
            alignment=ft.Alignment.CENTER,
            content=ft.Image(src=image_url, width=56, height=56, fit=ft.BoxFit.CONTAIN) if image_url else None,
            on_click=lambda _: self.__open_item_dialog(item),
        )
        available = self.__resolve_available(item, cart_quantities)
        available_text = ft.Text(f"{self._translation.get('available')}: {available}")
        self.__available_nodes[item.id] = available_text
        details = ft.Column(
            spacing=2,
            controls=[
                ft.Text(item.name, weight=ft.FontWeight.BOLD),
                ft.Text(f"{self._translation.get('index')}: {item.index}"),
                available_text,
                ft.Text(f"{self._translation.get('moq')}: {item.moq}"),
            ],
            expand=True,
        )
        details_container = ft.Container(content=details, expand=True, on_click=lambda _: self.__open_item_dialog(item))
        category_discount_container, category_discount_dropdown = self.__build_dropdown(
            key=f"category_discount_{item.id}",
            options=self.__build_discount_options(self.__get_category_discounts(item.category_id)),
            value="0",
        )
        category_discount_dropdown.label = self._translation.get("category_discount")
        item_discount_container, item_discount_dropdown = self.__build_dropdown(
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

        qty_input = NumericField(
            value=0,
            step=item.moq,
            precision=0,
            is_float=False,
            read_only=False,
            on_change=lambda event: self.__handle_quantity_change(event, item),
            expand=True,
        )
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
            on_click=lambda _: self.__on_add_to_cart_clicked(
                item,
                qty_input,
                category_discount_dropdown,
                item_discount_dropdown,
            ),
        )
        return ft.Container(
            padding=ft.Padding.all(8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                expand=True,
                controls=[
                    image,
                    details_container,
                    ft.Container(content=category_discount_container, expand=True),
                    ft.Container(content=item_discount_container, expand=True),
                    ft.Container(content=qty_input, expand=True),
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
        available = self.__resolve_available(item, self._controller.get_cart_quantities())
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
        available = self.__resolve_available(item, self._controller.get_cart_quantities())
        if int(quantity) > available:
            qty_input.error = self._translation.get("insufficient_stock")
            return
        qty_input.error = None
        category_discount_id = int(category_dropdown.value) if category_dropdown.value not in {"0", None} else None
        item_discount_id = int(item_dropdown.value) if item_dropdown.value not in {"0", None} else None
        self._controller.on_add_to_cart(
            item.id,
            int(quantity),
            item.category_id,
            category_discount_id,
            item_discount_id,
        )
        qty_input.value = 0
        qty_input.error = None
        self.__safe_update(qty_input)
        self.__toggle_add_button(qty_input, False)
        self.__update_available_for_item(item.id)

    def __on_category_changed(self) -> None:
        self.__refresh_items_list()

    def __on_checkout_back_clicked(self) -> None:
        self._controller._page.pop_dialog()
        self.open_cart_dialog()

    def __on_checkout_clicked(self) -> None:
        self._controller._page.pop_dialog()
        self._controller.on_checkout_requested()

    def __on_checkout_confirm_clicked(
        self,
        currency_dropdown: ft.Dropdown,
        customer_discount_dropdown: ft.Dropdown,
        delivery_method_dropdown: ft.Dropdown,
    ) -> None:
        def parse_dropdown(value: str | None) -> int | None:
            if not value or value in {"0", ""}:
                return None
            try:
                return int(value)
            except ValueError:
                return None

        currency_id = parse_dropdown(currency_dropdown.value)
        if currency_id is None:
            return
        customer_discount_id = parse_dropdown(customer_discount_dropdown.value)
        delivery_method_id = parse_dropdown(delivery_method_dropdown.value)
        self._controller._page.pop_dialog()
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
            self.__safe_update(dropdown)
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
        dialog = BaseDialog(
            title=None,
            controls=[ft.Image(src=url, width=800, height=800, fit=ft.BoxFit.CONTAIN)],
            actions=[
                ft.TextButton(self._translation.get("ok"), on_click=lambda _: self._controller._page.pop_dialog()),
            ],
        )
        self._controller._queue_dialog(dialog)

    def __open_item_dialog(self, item: OrderViewSourceItemSchema) -> None:
        available_quantity = max(0, item.stock_quantity - item.reserved_quantity)
        description = item.description
        is_fragile = item.is_fragile
        expiration_date = item.expiration_date
        category_name = item.category_name
        detail_rows: list[tuple[str, str]] = [
            ("name", item.name),
            ("index", item.index),
            ("ean", item.ean),
            ("description", description or ""),
            (
                "is_fragile",
                (
                    ""
                    if is_fragile is None
                    else self._translation.get("yes") if is_fragile else self._translation.get("no")
                ),
            ),
            ("expiration_date", "" if expiration_date is None else str(expiration_date)),
            ("category_name", category_name or ""),
            ("available", str(available_quantity)),
            ("vat_rate", str(item.vat_rate)),
            ("moq", str(item.moq)),
            ("dimensions", f"{item.width}x{item.height}x{item.length}"),
            ("weight", str(item.weight)),
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
        image_urls = self.__images_map.get(item.id, [])
        gallery_row: ft.Control | None = None
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

            def move_left(_: ft.ControlEvent) -> None:
                nonlocal start_index
                if start_index <= 0:
                    return
                start_index -= 1
                render_thumbnails()

            def move_right(_: ft.ControlEvent) -> None:
                nonlocal start_index
                if start_index + 3 >= len(image_urls):
                    return
                start_index += 1
                render_thumbnails()

            left_button = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=move_left, disabled=True)
            right_button = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=move_right, disabled=True)
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

    def __refresh_items_list(self) -> None:
        filtered_items = self.__filter_items_by_category(self.__items)
        cart_quantities = self._controller.get_cart_quantities()
        self.__available_nodes.clear()
        self.__items_list.controls = [self.__build_item_row(item, cart_quantities) for item in filtered_items]
        self.__safe_update(self.__items_list)

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

    def __remove_cart_item(self, item_id: int, refresh: Callable[[], None]) -> None:
        self._controller.remove_from_cart(item_id)
        self.__update_available_for_item(item_id)
        refresh()

    def __resolve_available(self, item: OrderViewSourceItemSchema, cart_quantities: dict[int, int]) -> int:
        base_available = max(0, item.stock_quantity - item.reserved_quantity)
        cart_quantity = cart_quantities.get(item.id, 0)
        return max(0, base_available - cart_quantity)

    def __resolve_discount_label(self, discount_id: int | None, discounts: list[OrderViewDiscountSchema]) -> str | None:
        if not isinstance(discount_id, int):
            return None
        for discount in discounts:
            if discount.id == discount_id:
                percent = (discount.percent or 0) * 100
                return f"{discount.code} ({percent:.0f}%)"
        return None

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        control.update()

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
                self.__safe_update(control.content)
                break

    def __update_available_for_item(self, item_id: int) -> None:
        item = self.__items_by_id.get(item_id)
        if not item:
            return
        node = self.__available_nodes.get(item_id)
        if not node:
            return
        available = self.__resolve_available(item, self._controller.get_cart_quantities())
        node.value = f"{self._translation.get('available')}: {available}"
        self.__safe_update(node)

    def __wrap_dropdown(self, dropdown: ft.Dropdown) -> FieldGroup:
        return FieldGroup(
            label=(ft.Container(), 0),
            input=(ft.Container(content=dropdown), 0),
            marker=(ft.Container(), 0),
        )
