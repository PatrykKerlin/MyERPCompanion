from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import BinsViewStyles, ButtonStyles, MobileCommonViewStyles, TypographyStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.bins_controller import BinsController
    from schemas.business.logistic.bin_schema import BinPlainSchema
    from schemas.business.logistic.item_schema import ItemPlainSchema


class BinsView(BaseView):
    def __init__(
        self,
        controller: BinsController,
        translation: Translation,
        view_key: View,
    ) -> None:
        super().__init__(controller, translation, view_key)
        self.__bins: list[BinPlainSchema] = []
        self.__selected_bin: BinPlainSchema | None = None
        self.__items: list[ItemPlainSchema] = []
        self.__item_quantities: dict[int, int] = {}
        self.__filter_query = ""
        self.__bin_direction_filter = "all"

        self.__title = self._get_label("", style=TypographyStyles.HEADER_TITLE)
        self.__filter_field = self._get_text_field(
            value="",
            on_change=lambda event: self._controller.on_value_changed("filter_query"),
            on_submit=lambda event: self._controller.on_value_changed("filter_query"),
            on_focus=lambda event: self._controller.on_value_changed("filter_query")
            if str(getattr(event, "data", "")).lower() == "false"
            else None,
            on_tap_outside=lambda event: self._controller.on_value_changed("filter_query"),
            expand=True,
        )
        self.__filter_field.col = self._responsive_col(BinsViewStyles.FILTER_TEXT_INPUT_SIZE)
        self.__filter_field.on_change = self.__on_filter_changed
        self.__filter_field.dense = True
        self.__filter_field.prefix_icon = ft.Icons.SEARCH

        self.__direction_filter_field = self._get_dropdown(
            options=[
                ("all", "All"),
                ("inbound", "Inbound"),
                ("outbound", "Outbound"),
            ],
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("bin_direction_filter", self.__on_bin_direction_filter_changed
            ),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__direction_filter_field.col = self._responsive_col(BinsViewStyles.FILTER_DIRECTION_INPUT_SIZE)
        self.__direction_filter_field.value = "all"

        self.__filters_row = ft.ResponsiveRow(
            controls=[self.__filter_field, self.__direction_filter_field],
            columns=BinsViewStyles.FILTER_ROW_COLUMNS,
            alignment=BinsViewStyles.FILTER_ROW_ALIGNMENT,
            vertical_alignment=BinsViewStyles.FILTER_ROW_VERTICAL_ALIGNMENT,
        )

        self._add_to_inputs(
            {
                "filter_query": self.__filter_field,
                "bin_direction_filter": self.__direction_filter_field,
            }
        )
        self.__list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=MobileCommonViewStyles.LIST_SPACING)
        self.__back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_back_click,
            style=ButtonStyles.primary_regular,
        )
        self.__header_texts = ft.Column(
            controls=[self.__title],
            spacing=MobileCommonViewStyles.HEADER_TEXTS_SPACING,
        )
        self.__header_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.__header_texts, col=MobileCommonViewStyles.HEADER_TEXTS_COL),
                ft.Container(
                    content=self.__back_button,
                    col=MobileCommonViewStyles.HEADER_ACTION_COL,
                    alignment=MobileCommonViewStyles.HEADER_BACK_ALIGNMENT,
                ),
            ],
            columns=MobileCommonViewStyles.HEADER_ROW_COLUMNS,
            alignment=MobileCommonViewStyles.HEADER_ROW_ALIGNMENT,
            vertical_alignment=MobileCommonViewStyles.HEADER_ROW_VERTICAL_ALIGNMENT,
        )

        self._master_column.controls = [
            self.__header_row,
            self.__filters_row,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__list,
        ]
        self.__render()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render()
        self.safe_update(self)

    def set_bins(self, bins: list[BinPlainSchema]) -> None:
        self.__bins = bins
        self.__selected_bin = None
        self.__items = []
        self.__item_quantities = {}
        self.__reset_filter()
        self.__render()
        self.safe_update(self)

    def set_bin_items(
        self,
        bin_schema: BinPlainSchema,
        items: list[ItemPlainSchema],
        item_quantities: dict[int, int],
    ) -> None:
        self.__selected_bin = bin_schema
        self.__items = items
        self.__item_quantities = item_quantities
        self.__reset_filter()
        self.__render()
        self.safe_update(self)

    def __render(self) -> None:
        if self.__selected_bin is None:
            self.__title.value = self._translation.get("bins")
            self.__filter_field.label = self._translation.get("bin_filter")
        else:
            self.__title.value = self._translation.get("items")
            self.__filter_field.label = self._translation.get("item_filter")
        self.__back_button.content = self._translation.get("back")
        self.__direction_filter_field.label = self._translation.get("bin_type_filter")
        self.__direction_filter_field.options = self.__build_direction_filter_options()
        self.__direction_filter_field.value = self.__bin_direction_filter
        self.__direction_filter_field.visible = self.__selected_bin is None
        self.__list.controls = self.__build_list_controls()

    def __build_direction_filter_options(self) -> list[ft.DropdownOption]:
        return [
            ft.dropdown.Option(key="all", text=self._translation.get("all")),
            ft.dropdown.Option(key="inbound", text=self._translation.get("inbound")),
            ft.dropdown.Option(key="outbound", text=self._translation.get("outbound")),
        ]

    def __build_list_controls(self) -> list[ft.Control]:
        if self.__selected_bin is None:
            filtered_bins = self.__get_filtered_bins()
            if not filtered_bins:
                return [self._get_label(self._translation.get("no_bins"), text_align=ft.TextAlign.CENTER)]
            controls: list[ft.Control] = []
            for bin_schema in filtered_bins:
                controls.append(
                    ft.Card(
                        bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                        content=ft.ListTile(
                            title=self._get_label(bin_schema.location),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                            on_click=self.__build_bin_click_handler(bin_schema.id),
                        )
                    )
                )
            return controls

        filtered_items = self.__get_filtered_items()
        if not filtered_items:
            return [self._get_label(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]
        controls = []
        for item_schema in filtered_items:
            quantity = self.__item_quantities.get(item_schema.id, 0)
            controls.append(
                ft.Card(
                    bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                    content=ft.ListTile(
                        title=self._get_label(item_schema.name),
                        subtitle=self._get_label(
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
        self.__bin_direction_filter = "all"
        self.__direction_filter_field.value = "all"

    def __get_filtered_bins(self) -> list[BinPlainSchema]:
        bins = self.__bins
        if self.__bin_direction_filter == "inbound":
            bins = [bin_schema for bin_schema in bins if bin_schema.is_inbound]
        elif self.__bin_direction_filter == "outbound":
            bins = [bin_schema for bin_schema in bins if bin_schema.is_outbound]

        if not self.__filter_query:
            return bins
        return [bin_schema for bin_schema in bins if self.__filter_query in bin_schema.location.lower()]

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

    def __on_filter_changed(self, _: ft.Event[ft.TextField]) -> None:
        self.__filter_query = (self.__filter_field.value or "").strip().lower()
        self.__list.controls = self.__build_list_controls()
        self.safe_update(self)

    def __on_bin_direction_filter_changed(self) -> None:
        selected = self.__direction_filter_field.value
        if selected in {"all", "inbound", "outbound"}:
            self.__bin_direction_filter = selected
        else:
            self.__bin_direction_filter = "all"
            self.__direction_filter_field.value = "all"
        self.__list.controls = self.__build_list_controls()
        self.safe_update(self)

    def __on_back_click(self, _: ft.Event[ft.Button]) -> None:
        if self.__selected_bin is None:
            self._controller.on_back_to_menu()
            return
        self.__selected_bin = None
        self.__reset_filter()
        self.__render()
        self.safe_update(self)
