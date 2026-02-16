from typing import Any, Callable, cast

import flet as ft
from controllers.base.base_controller import BaseController
from styles.colors import AppColors
from styles.components import ComponentStyles
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles
from views.base.base_component import BaseComponent


class BulkTransfer(ft.Container):
    def __init__(
        self,
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        source_label: str,
        target_label: str | None = None,
        on_move_requested: Callable[[list[int]], None] | None = None,
        on_delete_clicked: Callable[[list[int]], None] | None = None,
        on_pending_reverted: Callable[[list[int]], None] | None = None,
        allow_duplicate_targets: bool = False,
        source_columns: list[str] | None = None,
        target_columns: list[str] | None = None,
        height: int | None = None,
        cancel_label: str = "Cancel",
        confirm_label: str = "OK",
        delete_confirm_title: str = "Confirm",
        delete_confirm_message: str = "Delete selected item(s)?",
    ) -> None:
        super().__init__(expand=True)
        self.__source_enabled = False
        self.__target_enabled = False
        self.__buttons_enabled = False
        self.__allow_duplicate_targets = allow_duplicate_targets
        resolved_target_label = source_label if target_label is None else target_label
        target_label_text = target_label or ""
        self.__source_columns = source_columns or [source_label]
        self.__target_columns = target_columns or [resolved_target_label]
        self.__base_height = height
        if height is not None:
            self.height = height

        self.__source_rows: list[tuple[int, list[Any]]] = []
        self.__target_rows: list[tuple[int, list[Any]]] = []
        self.__target_ids: set[int] = set()
        self.__initial_target_ids: set[int] = set()
        self.__initial_target_rows: dict[int, list[Any]] = {}
        self.__source_selectable_ids: set[int] | None = None

        self.__selected_source_ids: set[int] = set()
        self.__selected_target_ids: set[int] = set()
        self.__moved_source_ids: set[int] = set()
        self.__pending_target_map: dict[int, int] = {}
        self.__next_pending_target_id = -1

        self.__on_save_clicked = on_save_clicked
        self.__on_move_requested = on_move_requested
        self.__on_delete_clicked = on_delete_clicked
        self.__on_pending_reverted = on_pending_reverted
        self.__cancel_label = cancel_label
        self.__confirm_label = confirm_label
        self.__delete_confirm_title = delete_confirm_title
        self.__delete_confirm_message = delete_confirm_message

        self.__source_container = ComponentStyles.outlined_container(expand=True)
        self.__target_container = ComponentStyles.outlined_container(expand=True)

        self.__button_move = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            disabled=True,
            on_click=self.__handle_move_clicked,
            style=ButtonStyles.icon,
        )
        self.__button_delete = ft.IconButton(
            icon=ft.Icons.DELETE,
            disabled=True,
            on_click=self.__handle_delete_clicked,
            style=ButtonStyles.icon,
        )
        self.__button_save = ft.IconButton(
            icon=ft.Icons.SAVE,
            disabled=True,
            on_click=self.__handle_save_clicked,
            style=ButtonStyles.icon,
        )

        source_column = ft.Column(
            controls=[
                ft.Text(source_label, weight=ft.FontWeight.W_600),
                self.__source_container,
            ],
            expand=True,
            spacing=AppDimensions.SPACE_XS,
        )

        buttons_column = ft.Column(
            controls=[self.__button_move, self.__button_delete, self.__button_save],
            alignment=AlignmentStyles.AXIS_CENTER,
            horizontal_alignment=AlignmentStyles.CROSS_CENTER,
            spacing=AppDimensions.SPACE_MD,
        )

        target_controls: list[ft.Control] = [
            ft.Text(target_label_text, weight=ft.FontWeight.W_600),
            self.__target_container,
        ]

        target_column = ft.Column(
            controls=target_controls,
            expand=True,
            spacing=AppDimensions.SPACE_XS,
        )

        self.content = ft.Row(
            controls=[source_column, buttons_column, target_column],
            expand=True,
            spacing=AppDimensions.SPACE_LG,
            vertical_alignment=AlignmentStyles.CROSS_STRETCH,
        )
        self.__render_source_table()
        self.__render_target_table()

    def update(self) -> None:
        if not self.visible:
            self.height = 0
        elif self.__base_height is not None:
            self.height = self.__base_height
        super().update()

    def clear_pending_changes(self) -> None:
        pending_ids = [target_id for target_id in self.__pending_target_map]
        if pending_ids:
            self.remove_target_items(pending_ids)
        self.__selected_source_ids.clear()
        self.__selected_target_ids.clear()
        self.__moved_source_ids.clear()
        self.__pending_target_map.clear()
        self.__update_save_button_state()
        self.__render_source_table()
        self.__render_target_table()

    def set_enabled_states(self, source_enabled: bool, target_enabled: bool, buttons_enabled: bool) -> None:
        self.__source_enabled = source_enabled
        self.__target_enabled = target_enabled
        self.__buttons_enabled = buttons_enabled
        self.__update_action_buttons()
        self.__update_save_button_state()
        self.__render_source_table()
        self.__render_target_table()

    def set_source_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(enabled, self.__target_enabled, enabled and self.__target_enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(self.__source_enabled, enabled, self.__source_enabled and enabled)

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        rows = [(item_id, [label]) for item_id, label in items]
        self.set_source_rows(cast(list[tuple[int, list[Any]]], rows))

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        rows = [(item_id, [label]) for item_id, label in items]
        self.set_target_rows(cast(list[tuple[int, list[Any]]], rows))

    def set_source_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__source_rows = rows
        self.__selected_source_ids.clear()
        self.__moved_source_ids.clear()
        self.__render_source_table()
        self.__update_save_button_state()

    def set_source_selectable_ids(self, selectable_ids: set[int] | None) -> None:
        self.__source_selectable_ids = selectable_ids
        self.__render_source_table()

    def set_target_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__target_rows = rows
        self.__target_ids = {item_id for item_id, _ in rows}
        self.__initial_target_ids = set(self.__target_ids)
        self.__initial_target_rows = {item_id: values[:] for item_id, values in rows}
        self.__selected_target_ids.clear()
        self.__pending_target_map.clear()
        self.__moved_source_ids.clear()
        self.__render_target_table()
        self.__update_save_button_state()

    def add_target_row(self, source_id: int, values: list[Any], highlight: bool = True) -> int:
        target_id = self.__next_pending_target_id
        self.__next_pending_target_id -= 1
        self.__pending_target_map[target_id] = source_id
        self.__target_rows = [(target_id, values)] + self.__target_rows
        self.__target_ids.add(target_id)
        if highlight:
            self.__moved_source_ids.add(source_id)
        self.__selected_source_ids.clear()
        self.__selected_target_ids.clear()
        self.__selected_target_ids.add(target_id)
        self.__render_source_table()
        self.__render_target_table()
        self.__update_save_button_state()
        return target_id

    def add_target_rows_from_source(self, source_ids: list[int], highlight: bool = True) -> list[int]:
        items_to_move = self.get_source_items_by_ids(source_ids)
        if not items_to_move:
            return []
        created_target_ids: list[int] = []
        for source_id, values in items_to_move:
            created_target_ids.append(self.add_target_row(source_id, values, highlight=highlight))
        return created_target_ids

    def update_existing_target(self, target_id: int, source_id: int, values: list[Any]) -> None:
        for index, (item_id, _) in enumerate(self.__target_rows):
            if item_id == target_id:
                self.__target_rows[index] = (item_id, values)
                break
        self.__pending_target_map[target_id] = source_id
        self.__moved_source_ids.add(source_id)
        self.__selected_source_ids.clear()
        self.__selected_target_ids.clear()
        self.__selected_target_ids.add(target_id)
        self.__render_source_table()
        self.__render_target_table()
        self.__update_save_button_state()

    def update_target_row_values(self, target_id: int, values: list[Any]) -> None:
        for index, (item_id, _) in enumerate(self.__target_rows):
            if item_id == target_id:
                self.__target_rows[index] = (item_id, values)
                break
        self.__render_target_table()
        self.__update_action_buttons()

    def prepend_target_items(self, items: list[tuple[int, list[Any]]], highlight: bool) -> None:
        if not items:
            return
        new_items = [(item_id, label) for item_id, label in items if item_id not in self.__target_ids]
        if not new_items:
            return
        self.__target_rows = new_items + self.__target_rows
        self.__target_ids.update(item_id for item_id, _ in new_items)
        if highlight:
            new_ids = [item_id for item_id, _ in new_items]
            self.__moved_source_ids.update(new_ids)
            self.__selected_target_ids.difference_update(new_ids)
            self.__render_source_table()
        self.__render_target_table()
        self.__update_save_button_state()

    def remove_source_items(self, ids: list[int]) -> None:
        ids_set = set(ids)
        self.__source_rows = [(item_id, label) for item_id, label in self.__source_rows if item_id not in ids_set]
        self.__selected_source_ids.difference_update(ids_set)
        self.__render_source_table()

    def remove_target_items(self, ids: list[int]) -> None:
        ids_set = set(ids)
        pending_source_ids = {
            self.__pending_target_map[target_id] for target_id in ids_set if target_id in self.__pending_target_map
        }
        self.__target_rows = [(item_id, label) for item_id, label in self.__target_rows if item_id not in ids_set]
        self.__target_ids.difference_update(ids_set)
        self.__selected_target_ids.difference_update(ids_set)
        for target_id in ids_set:
            self.__pending_target_map.pop(target_id, None)
        for source_id in pending_source_ids:
            if source_id not in self.__pending_target_map.values():
                self.__moved_source_ids.discard(source_id)
        self.__render_target_table()
        self.__render_source_table()
        self.__update_save_button_state()

    def get_selected_source_ids(self) -> list[int]:
        return list(self.__selected_source_ids)

    def get_selected_target_ids(self) -> list[int]:
        return list(self.__selected_target_ids)

    def get_source_items_by_ids(self, ids: list[int]) -> list[tuple[int, list[Any]]]:
        ids_set = set(ids)
        return [(item_id, label) for item_id, label in self.__source_rows if item_id in ids_set]

    def is_target_item_from_source(self, item_id: int) -> bool:
        return item_id in self.__pending_target_map

    def has_target_item(self, item_id: int) -> bool:
        if self.__allow_duplicate_targets:
            return False
        return item_id in self.__target_ids

    def mark_source_items_as_moved(self, ids: list[int]) -> None:
        if not ids:
            return
        self.__moved_source_ids.update(ids)
        self.__render_source_table()
        self.__update_save_button_state()

    def get_pending_move_ids(self) -> list[int]:
        return list(self.__pending_target_map.values())

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return list(self.__pending_target_map.items())

    def move_source_items(self, ids_to_add: list[int], highlight: bool) -> list[int]:
        if not ids_to_add:
            return []
        created_target_ids: list[int] = []
        if self.__allow_duplicate_targets:
            items_to_move = self.get_source_items_by_ids(ids_to_add)
            if not items_to_move:
                return []
            for source_id, label in items_to_move:
                created_target_ids.append(self.add_target_row(source_id, label, highlight=highlight))
            return created_target_ids
        existing_ids = [item_id for item_id in ids_to_add if self.has_target_item(item_id)]
        new_ids = [item_id for item_id in ids_to_add if item_id not in existing_ids]
        if existing_ids:
            self.mark_source_items_as_moved(existing_ids)
            self.__render_target_table()
        if not new_ids:
            return []
        items_to_move = self.get_source_items_by_ids(new_ids)
        if not items_to_move:
            return []
        actual_ids = [item_id for item_id, _ in items_to_move]
        if not actual_ids:
            return []
        for item_id in actual_ids:
            self.__pending_target_map[item_id] = item_id
        self.prepend_target_items(items_to_move, highlight=highlight)
        self.__selected_source_ids.clear()
        self.__selected_target_ids.clear()
        self.__selected_target_ids.update(actual_ids)
        self.__update_save_button_state()
        return actual_ids

    def __restore_target_row(self, target_id: int) -> None:
        initial_values = self.__initial_target_rows.get(target_id)
        if initial_values is None:
            return
        for index, (item_id, _) in enumerate(self.__target_rows):
            if item_id == target_id:
                self.__target_rows[index] = (item_id, initial_values[:])
                return

    def __render_source_table(self) -> None:
        if not self.__source_container:
            return
        selectable_ids = (
            {item_id for item_id, _ in self.__source_rows}
            if (self.__buttons_enabled and self.__source_enabled)
            else set()
        )
        if self.__source_selectable_ids is not None:
            selectable_ids &= self.__source_selectable_ids
        table = self.__build_table(
            columns=self.__source_columns,
            rows=self.__source_rows,
            selected_ids=self.__selected_source_ids,
            highlighted_ids=self.__moved_source_ids,
            selectable_ids=selectable_ids,
            on_row_selected=self.__toggle_source_selection,
        )
        self.__source_container.content = table
        self.__update_action_buttons()
        BaseComponent.safe_update(self)

    def __render_target_table(self) -> None:
        if not self.__target_container:
            return
        highlighted_ids = {item_id for item_id, _ in self.__target_rows if self.is_target_item_from_source(item_id)}
        if self.__on_delete_clicked is not None:
            selectable_ids = {item_id for item_id, _ in self.__target_rows}
        else:
            selectable_ids = highlighted_ids
        if not (self.__buttons_enabled and self.__target_enabled):
            selectable_ids = set()
        table = self.__build_table(
            columns=self.__target_columns,
            rows=self.__target_rows,
            selected_ids=self.__selected_target_ids,
            highlighted_ids=highlighted_ids,
            selectable_ids=selectable_ids,
            on_row_selected=self.__toggle_target_selection,
        )
        self.__target_container.content = table
        self.__update_action_buttons()
        BaseComponent.safe_update(self)

    def __normalize_row_values(self, values: list[Any], column_count: int) -> list[Any]:
        if len(values) >= column_count:
            return values[:column_count]
        return values + [""] * (column_count - len(values))

    def __build_table(
        self,
        columns: list[str],
        rows: list[tuple[int, list[Any]]],
        selected_ids: set[int],
        highlighted_ids: set[int],
        selectable_ids: set[int],
        on_row_selected: Callable[[int], None],
    ) -> ft.ListView:
        table_columns = [ft.DataColumn(label=ft.Text(""))]
        table_columns.extend([ft.DataColumn(label=ft.Text(col)) for col in columns])
        table_rows: list[ft.DataRow] = []
        for item_id, values in rows:
            row_values = self.__normalize_row_values(values, len(columns))
            is_selected = item_id in selected_ids
            is_highlighted = item_id in highlighted_ids
            selection_cell = ft.DataCell(
                ft.Checkbox(
                    value=is_selected,
                    disabled=item_id not in selectable_ids,
                    on_change=(
                        (lambda _, item_id=item_id: on_row_selected(item_id))
                        if item_id in selectable_ids
                        else None
                    ),
                )
            )
            cells: list[ft.DataCell] = []
            for value in row_values:
                if isinstance(value, ft.Control):
                    cells.append(ft.DataCell(value))
                else:
                    text_value = "" if value is None else str(value)
                    cells.append(
                        ft.DataCell(
                            ft.Text(text_value, no_wrap=True, color=AppColors.ERROR if is_highlighted else None)
                        )
                    )
            table_rows.append(ft.DataRow(cells=[selection_cell] + cells))
        data_table = ft.DataTable(
            columns=table_columns,
            rows=table_rows,
            show_checkbox_column=False,
        )
        horizontal_scroller = ft.Row(controls=[data_table], scroll=ft.ScrollMode.AUTO, expand=True)
        vertical_scroller = ft.ListView(
            controls=[horizontal_scroller],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        return vertical_scroller

    def __toggle_source_selection(self, item_id: int) -> None:
        if item_id in self.__selected_source_ids:
            self.__selected_source_ids.remove(item_id)
        else:
            self.__selected_source_ids.clear()
            self.__selected_source_ids.add(item_id)
        self.__update_action_buttons()
        self.__render_source_table()

    def __toggle_target_selection(self, item_id: int) -> None:
        if item_id in self.__selected_target_ids:
            self.__selected_target_ids.remove(item_id)
        else:
            self.__selected_target_ids.clear()
            self.__selected_target_ids.add(item_id)
        self.__update_action_buttons()
        self.__render_target_table()

    def __handle_move_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        selected_ids = self.get_selected_source_ids()
        if not selected_ids:
            return
        if self.__on_move_requested:
            self.__on_move_requested(selected_ids)
            return
        self.move_source_items(selected_ids, highlight=True)

    def __handle_delete_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        selected_ids = self.get_selected_target_ids()
        if not selected_ids:
            return
        page = getattr(self, "page", None)
        if page is None:
            return
        self.__show_delete_confirm(page, selected_ids)

    def __execute_delete(self, selected_ids: list[int]) -> None:
        moved_ids = [item_id for item_id in selected_ids if self.is_target_item_from_source(item_id)]
        moved_existing_ids = [item_id for item_id in moved_ids if item_id in self.__initial_target_ids]
        moved_new_ids = [item_id for item_id in moved_ids if item_id not in moved_existing_ids]
        persisted_ids = [item_id for item_id in selected_ids if item_id not in moved_ids]
        if moved_new_ids:
            self.remove_target_items(moved_new_ids)
        if moved_existing_ids:
            for target_id in moved_existing_ids:
                source_id = self.__pending_target_map.pop(target_id, None)
                if source_id is not None and source_id not in self.__pending_target_map.values():
                    self.__moved_source_ids.discard(source_id)
                self.__restore_target_row(target_id)
            self.__selected_target_ids.difference_update(moved_existing_ids)
            self.__render_target_table()
        if self.__on_pending_reverted:
            reverted_ids = moved_existing_ids + moved_new_ids
            if reverted_ids:
                self.__on_pending_reverted(reverted_ids)
        if persisted_ids:
            if self.__on_delete_clicked:
                self.__on_delete_clicked(persisted_ids)
            self.__selected_target_ids.difference_update(persisted_ids)
            self.__render_target_table()

    def __show_delete_confirm(self, page: ft.Page, selected_ids: list[int]) -> None:
        def on_cancel() -> None:
            page.pop_dialog()

        def on_confirm() -> None:
            page.pop_dialog()
            self.__execute_delete(selected_ids)

        actions: list[ft.Control] = [
            ft.TextButton(self.__cancel_label, on_click=lambda _: on_cancel(), style=ButtonStyles.compact),
            ft.TextButton(self.__confirm_label, on_click=lambda _: on_confirm(), style=ButtonStyles.primary_compact),
        ]

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.__delete_confirm_title),
            content=ft.Text(self.__delete_confirm_message),
            actions=actions,
        )
        BaseController.queue_dialog(page, dialog)

    def __handle_save_clicked(self, event: ft.Event[ft.IconButton]) -> None:
        self.__on_save_clicked(event)

    def __update_save_button_state(self) -> None:
        has_pending = bool(self.__pending_target_map)
        self.__button_save.disabled = not (self.__buttons_enabled and has_pending)
        BaseComponent.safe_update(self)

    def __update_action_buttons(self) -> None:
        has_source_selection = bool(self.__selected_source_ids)
        has_target_selection = bool(self.__selected_target_ids)
        self.__button_move.disabled = not (self.__buttons_enabled and self.__source_enabled and has_source_selection)
        self.__button_delete.disabled = not (self.__buttons_enabled and self.__target_enabled and has_target_selection)
