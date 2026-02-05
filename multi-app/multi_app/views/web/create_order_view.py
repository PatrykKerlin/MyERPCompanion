from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from schemas.business.trade.order_view_schema import (
    OrderViewCategorySchema,
    OrderViewDiscountSchema,
    OrderViewSourceItemSchema,
)
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.base.base_dialog import BaseDialog
from views.controls.numeric_field_control import NumericField
from utils.field_group import FieldGroup

if TYPE_CHECKING:
    from controllers.web.create_order_controller import CreateOrderController


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
        self.__item_price_nodes: dict[int, tuple[ft.Text, ft.Text]] = {}
        self.__item_discount_dropdowns: dict[int, ft.Dropdown] = {}
        self.__item_category_dropdowns: dict[int, ft.Dropdown] = {}
        self.__items_by_id: dict[int, OrderViewSourceItemSchema] = {item.id: item for item in items}
        self.__category_dropdown_container, self.__category_dropdown = self.__build_dropdown(
            key="category_id",
            options=self.__build_category_options(),
            callbacks=[self.__on_category_changed],
            value="0",
        )
        self._inputs["category_id"] = self.__wrap_dropdown(self.__category_dropdown)
        self.__items_list = ft.ListView(spacing=8, expand=True)
        self.__refresh_items_list()

        header_row = ft.ResponsiveRow(
            columns=12,
            controls=[self.__category_dropdown_container],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.content = ft.Column(
            expand=True,
            controls=[
                header_row,
                ft.Container(height=8),
                self.__items_list,
            ],
        )

    def __build_category_options(self) -> list[tuple[int | str, str]]:
        options: list[tuple[int | str, str]] = [(category.id, category.label) for category in self.__categories]
        return options

    def __build_discount_options(self, discounts: list[OrderViewDiscountSchema]) -> list[tuple[int | str, str]]:
        return [
            (discount.id, f"{discount.code} ({(discount.percent or 0) * 100:.0f}%)")
            for discount in discounts
        ]

    def __on_category_changed(self) -> None:
        self.__refresh_items_list()

    def __refresh_items_list(self) -> None:
        filtered_items = self.__filter_items_by_category(self.__items)
        self.__items_list.controls = [self.__build_item_row(item) for item in filtered_items]
        self.__safe_update(self.__items_list)

    def __filter_items_by_category(self, items: list[OrderViewSourceItemSchema]) -> list[OrderViewSourceItemSchema]:
        selected = self.__category_dropdown.value
        if not selected or selected in {"0", "all"}:
            return list(items)
        try:
            category_id = int(selected)
        except ValueError:
            return list(items)
        return [item for item in items if item.category_id == category_id]

    def __build_item_row(self, item: OrderViewSourceItemSchema) -> ft.Control:
        image_url = self.__image_map.get(item.id)
        image = ft.Container(
            width=64,
            height=64,
            alignment=ft.Alignment.CENTER,
            content=ft.Image(src=image_url, width=56, height=56, fit=ft.BoxFit.CONTAIN) if image_url else None,
            on_click=lambda _: self.__open_item_dialog(item),
        )
        available = max(0, item.stock_quantity - item.reserved_quantity)
        details = ft.Column(
            spacing=2,
            controls=[
                ft.Text(item.name, weight=ft.FontWeight.BOLD),
                ft.Text(f"{self._translation.get('index')}: {item.index}"),
                ft.Text(f"{self._translation.get('available')}: {available}"),
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
            on_change=lambda event: self.__handle_quantity_change(event, item.moq),
            expand=True,
        )
        net_text = ft.Text("")
        gross_text = ft.Text("")
        self.__item_price_nodes[item.id] = (net_text, gross_text)
        update_prices = lambda: self.__update_price_texts(
            item,
            category_discount_dropdown,
            item_discount_dropdown,
            net_text,
            gross_text,
        )
        update_prices()
        category_discount_dropdown.on_select = lambda _: self.__on_item_category_discount_changed(
            item,
            category_discount_dropdown,
            update_prices,
        )
        item_discount_dropdown.on_select = lambda _: update_prices()
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
                    ft.Column(
                        spacing=2,
                        controls=[net_text, gross_text],
                        expand=True,
                    ),
                    ft.Container(content=add_button, expand=True),
                ],
            ),
            expand=True,
        )

    def __resolve_item_discount(self, discounts: list[OrderViewDiscountSchema]) -> str | None:
        return "0"

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

    def __set_dropdown_options(self, dropdown: ft.Dropdown, options: list[tuple[int | str, str]]) -> None:
        dropdown.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in options
        ]

    def __wrap_dropdown(self, dropdown: ft.Dropdown) -> FieldGroup:
        return FieldGroup(
            label=(ft.Container(), 0),
            input=(ft.Container(content=dropdown), 0),
            marker=(ft.Container(), 0),
        )

    def __get_category_discounts(self, category_id: int | None) -> list[OrderViewDiscountSchema]:
        if category_id is None:
            return []
        category = next((item for item in self.__categories if item.id == category_id), None)
        return list(category.discounts) if category else []

    def __discount_percent(self, discounts: list[OrderViewDiscountSchema], selected: str | None) -> float:
        if not selected or selected == "0":
            return 0.0
        try:
            selected_id = int(selected)
        except ValueError:
            return 0.0
        for discount in discounts:
            if discount.id == selected_id and discount.percent is not None:
                return float(discount.percent) * 100.0
        return 0.0

    def __update_price_texts(
        self,
        item: OrderViewSourceItemSchema,
        category_dropdown: ft.Dropdown,
        item_dropdown: ft.Dropdown,
        net_text: ft.Text,
        gross_text: ft.Text,
    ) -> None:
        category_percent = self.__discount_percent(
            self.__get_category_discounts(item.category_id), category_dropdown.value
        )
        item_percent = self.__discount_percent(item.discounts, item_dropdown.value)
        total_percent = category_percent + item_percent
        net = item.purchase_price * (1 - total_percent / 100.0)
        gross = net * (1 + item.vat_rate / 100.0)
        net_text.value = f"{self._translation.get('net_price')}: {net:.2f}"
        gross_text.value = f"{self._translation.get('gross_price')}: {gross:.2f}"
        self.__safe_update(net_text)
        self.__safe_update(gross_text)

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
        for item_id in self.__category_discount_items.get(item.category_id, []):
            self.__refresh_item_price(item_id)
        self._controller.on_category_discount_changed(item.category_id, selected_value)
        update_prices()

    def __refresh_item_price(self, item_id: int) -> None:
        nodes = self.__item_price_nodes.get(item_id)
        if not nodes:
            return
        item = self.__items_by_id.get(item_id)
        if not item:
            return
        category_dropdown = self.__item_category_dropdowns.get(item_id)
        item_dropdown = self.__item_discount_dropdowns.get(item_id)
        if category_dropdown and item_dropdown:
            self.__update_price_texts(item, category_dropdown, item_dropdown, nodes[0], nodes[1])

    def __handle_quantity_change(self, event: ft.ControlEvent, moq: int) -> None:
        control = event.control
        if not isinstance(control, NumericField):
            return
        value = control.value
        if value is None or value == 0:
            control.error = None
            self.__toggle_add_button(control, False)
            return
        if int(value) % moq != 0:
            control.error = self._translation.get("invalid_quantity")
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

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        control.update()

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
                ""
                if is_fragile is None
                else self._translation.get("yes")
                if is_fragile
                else self._translation.get("no"),
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

    def __open_image_dialog(self, url: str) -> None:
        dialog = BaseDialog(
            title=None,
            controls=[ft.Image(src=url, width=800, height=800, fit=ft.BoxFit.CONTAIN)],
            actions=[
                ft.TextButton(self._translation.get("ok"), on_click=lambda _: self._controller._page.pop_dialog()),
            ],
        )
        self._controller._queue_dialog(dialog)
