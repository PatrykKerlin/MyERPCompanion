from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import flet as ft

from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.mobile.bins_controller import BinsController
    from schemas.business.logistic.bin_schema import BinPlainSchema
    from schemas.business.logistic.item_schema import ItemPlainSchema


class BinsView(BaseView):
    __MODE_BINS = "bins"
    __MODE_ITEMS = "items"

    def __init__(
        self,
        controller: BinsController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
    ) -> None:
        super().__init__(controller, translation, mode, view_key, data_row, 0, 0)
        self.__mode = self.__MODE_BINS
        self.__bins: list[BinPlainSchema] = []
        self.__selected_bin: BinPlainSchema | None = None
        self.__items: list[ItemPlainSchema] = []
        self.__item_quantities: dict[int, int] = {}
        self.__filter_query = ""

        self.__title = ft.Text(size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.__subtitle = ft.Text(size=14, text_align=ft.TextAlign.CENTER)
        filter_container, _ = self._get_text_input("filter_query", 12)
        self.__filter_field = cast(ft.TextField, filter_container.content)
        self.__filter_field.on_change = self.__on_filter_changed
        self.__filter_field.dense = True
        self.__filter_field.prefix_icon = ft.Icons.SEARCH
        self._add_to_inputs(
            {
                "filter_query": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(filter_container, 12),
                    marker=(ft.Container(), 0),
                )
            }
        )
        self.__list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=8)
        self.__back_button = ft.Button(on_click=self.__on_back_click, width=220)

        self._master_column.controls = [
            self.__title,
            self.__subtitle,
            filter_container,
            ft.Divider(height=1),
            self.__list,
            ft.Container(height=8),
            ft.Row(
                controls=[self.__back_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
        self.__render()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render()
        self.__update_if_attached()

    def set_bins(self, bins: list[BinPlainSchema]) -> None:
        self.__bins = bins
        self.__selected_bin = None
        self.__items = []
        self.__item_quantities = {}
        self.__mode = self.__MODE_BINS
        self.__reset_filter()
        self.__render()
        self.__update_if_attached()

    def set_bin_items(
        self,
        bin_schema: BinPlainSchema,
        items: list[ItemPlainSchema],
        item_quantities: dict[int, int],
    ) -> None:
        self.__selected_bin = bin_schema
        self.__items = items
        self.__item_quantities = item_quantities
        self.__mode = self.__MODE_ITEMS
        self.__reset_filter()
        self.__render()
        self.__update_if_attached()

    def __render(self) -> None:
        self.__title.value = self.__resolve_title()
        self.__subtitle.value = self.__resolve_subtitle()
        self.__filter_field.label = self.__resolve_filter_label()
        self.__back_button.content = self.__resolve_back_label()
        self.__list.controls = self.__build_list_controls()

    def __resolve_title(self) -> str:
        if self.__mode == self.__MODE_BINS:
            return self._translation.get("bins")
        return self._translation.get("items")

    def __resolve_subtitle(self) -> str:
        if self.__mode == self.__MODE_BINS:
            return self._translation.get("select_bin")
        if self.__selected_bin:
            return f"{self._translation.get('location')}: {self.__selected_bin.location}"
        return ""

    def __resolve_back_label(self) -> str:
        if self.__mode == self.__MODE_BINS:
            return self._translation.get("back_to_menu")
        return self._translation.get("back_to_bins")

    def __resolve_filter_label(self) -> str:
        if self.__mode == self.__MODE_BINS:
            return self._translation.get("bin_filter")
        return self._translation.get("item_filter")

    def __build_list_controls(self) -> list[ft.Control]:
        if self.__mode == self.__MODE_BINS:
            filtered_bins = self.__get_filtered_bins()
            if not filtered_bins:
                return [ft.Text(self._translation.get("no_bins"), text_align=ft.TextAlign.CENTER)]
            controls: list[ft.Control] = []
            for bin_schema in filtered_bins:
                controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(bin_schema.location),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                            on_click=self.__build_bin_click_handler(bin_schema.id),
                        )
                    )
                )
            return controls

        filtered_items = self.__get_filtered_items()
        if not filtered_items:
            return [ft.Text(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]
        controls = []
        for item_schema in filtered_items:
            quantity = self.__item_quantities.get(item_schema.id, 0)
            controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(item_schema.name),
                        subtitle=ft.Text(
                            f"{self._translation.get('index')}: {item_schema.index} | "
                            f"{self._translation.get('quantity')}: {quantity}",
                        ),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=self.__build_item_click_handler(item_schema.id),
                    )
                )
            )
        return controls

    def __build_bin_click_handler(self, bin_id: int):
        return lambda _: self._controller.on_bin_selected(bin_id)

    def __build_item_click_handler(self, item_id: int):
        return lambda _: self._controller.on_item_selected(item_id)

    def __reset_filter(self) -> None:
        self.__filter_query = ""
        self.__filter_field.value = ""

    def __get_filtered_bins(self) -> list[BinPlainSchema]:
        if not self.__filter_query:
            return self.__bins
        return [bin_schema for bin_schema in self.__bins if self.__filter_query in bin_schema.location.lower()]

    def __get_filtered_items(self) -> list[ItemPlainSchema]:
        if not self.__filter_query:
            return self.__items
        return [
            item_schema
            for item_schema in self.__items
            if self.__filter_query in item_schema.name.lower()
            or self.__filter_query in item_schema.index.lower()
            or self.__filter_query in item_schema.ean.lower()
        ]

    def __on_filter_changed(self, _: ft.ControlEvent) -> None:
        self.__filter_query = (self.__filter_field.value or "").strip().lower()
        self.__list.controls = self.__build_list_controls()
        self.__update_if_attached()

    def __on_back_click(self, _: ft.ControlEvent) -> None:
        if self.__mode == self.__MODE_BINS:
            self._controller.on_back_to_menu()
            return
        self.__mode = self.__MODE_BINS
        self.__reset_filter()
        self.__render()
        self.__update_if_attached()

    def __update_if_attached(self) -> None:
        try:
            self.update()
        except RuntimeError:
            return
