from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.mixins.group_bulk_transfer_mixin import GroupBulkTransferMixin
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from controllers.core.module_controller import ModuleController


class ModuleView(BaseView, GroupBulkTransferMixin):
    def __init__(
        self,
        controller: ModuleController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        source_views: list[tuple[int, list[str]]],
        target_views: list[tuple[int, list[str]]],
        group_source_rows: list[tuple[int, list[str]]],
        group_target_rows: list[tuple[int, list[str]]],
        on_views_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_views_delete_clicked: Callable[[list[int]], None] | None = None,
        on_groups_save_clicked=None,
        on_groups_delete_clicked=None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__pending_source_views = list(source_views)
        self.__pending_target_views = list(target_views)
        self.__target_rows: list[tuple[int, list[str]]] = []
        main_fields_definitions = [
            {"key": "key", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "in_side_menu", "input": self._get_checkbox, "input_size": 2},
            {"key": "order", "input": self._get_numeric_input},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid, expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self.__bulk_transfer = BulkTransfer(
            on_save_clicked=on_views_save_clicked or (lambda _: None),
            source_label=self._translation.get("available_views"),
            target_label=self._translation.get("module_views"),
            on_delete_clicked=on_views_delete_clicked,
            source_columns=[
                self._translation.get("key"),
                self._translation.get("description"),
                self._translation.get("order"),
            ],
            target_columns=[
                self._translation.get("key"),
                self._translation.get("description"),
                self._translation.get("order"),
            ],
        )
        self.__bulk_transfer.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        bulk_transfer_row = ft.Row(controls=[self.__bulk_transfer])
        self._init_group_bulk_transfer(
            mode=mode,
            source_rows=group_source_rows,
            target_rows=group_target_rows,
            source_label=self._translation.get("available_groups"),
            target_label=self._translation.get("module_groups"),
            on_save_clicked=on_groups_save_clicked,
            on_delete_clicked=on_groups_delete_clicked,
            height=260,
            visible_modes={ViewMode.READ, ViewMode.EDIT},
        )
        group_row = self._build_group_bulk_transfer_row()
        self._master_column.controls.extend(
            [
                self._columns_row,
                ft.Row(height=25),
                bulk_transfer_row,
                ft.Row(height=25),
                group_row,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )

    def did_mount(self):
        result = super().did_mount()
        self.__bulk_transfer.set_source_rows(cast(list[tuple[int, list[Any]]], self.__pending_source_views))
        self.__target_rows = list(self.__pending_target_views)
        self.__bulk_transfer.set_target_rows(cast(list[tuple[int, list[Any]]], self.__pending_target_views))
        self._mount_group_bulk_transfer()
        return result

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self.__bulk_transfer.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()
        if self.__bulk_transfer.page:
            self.__bulk_transfer.update()
        self._update_group_bulk_transfer_mode(mode)

    def set_source_views(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_source_rows(cast(list[tuple[int, list[Any]]], rows))

    def set_target_views(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__target_rows = list(rows)
        self.__bulk_transfer.set_target_rows(cast(list[tuple[int, list[Any]]], rows))

    def get_pending_view_targets(self) -> list[tuple[int, int]]:
        return self.__bulk_transfer.get_pending_targets()

    def get_target_key_by_id(self, item_id: int) -> str | None:
        for target_id, values in self.__target_rows:
            if target_id == item_id and values:
                return values[0]
        return None

    def __set_bulk_transfer_state(self, mode: ViewMode) -> None:
        enabled = mode == ViewMode.READ
        self.__bulk_transfer.set_enabled_states(enabled, enabled, enabled)
