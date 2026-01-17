import flet as ft
from typing import Callable


class BulkTransfer(ft.Container):
    def __init__(
        self,
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        source_label: str,
        target_label: str,
        on_move_requested: Callable[[list[int]], None] | None = None,
        on_delete_clicked: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(expand=True)
        self.__source_enabled = False
        self.__target_enabled = False
        self.__buttons_enabled = False

        self.__source_items: list[tuple[int, str]] = []
        self.__target_items: list[tuple[int, str]] = []
        self.__target_item_ids: set[int] = set()
        self.__initial_target_item_ids: set[int] = set()
        self.__selected_source_ids: set[int] = set()
        self.__selected_target_ids: set[int] = set()
        self.__source_ids_to_move: set[int] = set()

        self.__on_save_clicked = on_save_clicked
        self.__on_move_requested = on_move_requested
        self.__on_delete_clicked = on_delete_clicked

        self.__source_list = ft.ListView(expand=True, spacing=2, auto_scroll=False, disabled=True)
        self.__target_list = ft.ListView(expand=True, spacing=2, auto_scroll=False, disabled=True)

        self.__button_move = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD, disabled=True, on_click=self.__handle_move_clicked
        )
        self.__button_delete = ft.IconButton(icon=ft.Icons.DELETE, disabled=True, on_click=self.__handle_delete_clicked)
        self.__button_save = ft.IconButton(icon=ft.Icons.SAVE, disabled=True, on_click=self.__handle_save_clicked)

        source_column = ft.Column(
            controls=[
                ft.Text(source_label, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=self.__source_list,
                    expand=True,
                    border=ft.Border.all(1, ft.Colors.OUTLINE),
                    border_radius=6,
                    padding=6,
                ),
            ],
            expand=True,
            spacing=8,
        )

        buttons_column = ft.Column(
            controls=[self.__button_move, self.__button_delete, self.__button_save],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        target_column = ft.Column(
            controls=[
                ft.Text(target_label, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=self.__target_list,
                    expand=True,
                    border=ft.Border.all(1, ft.Colors.OUTLINE),
                    border_radius=6,
                    padding=6,
                ),
            ],
            expand=True,
            spacing=8,
        )

        self.content = ft.Row(
            controls=[source_column, buttons_column, target_column],
            expand=True,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def clear_pending_changes(self) -> None:
        ids_to_remove = [
            item_id for item_id in self.__source_ids_to_move if item_id not in self.__initial_target_item_ids
        ]
        if ids_to_remove:
            self.remove_target_items(ids_to_remove)
        self.__selected_source_ids.clear()
        self.__selected_target_ids.clear()
        self.__source_ids_to_move.clear()
        self.__update_save_button_state()
        self.__render_source_list()
        self.__render_target_list()

    def set_enabled_states(self, source_enabled: bool, target_enabled: bool, buttons_enabled: bool) -> None:
        self.__source_enabled = source_enabled
        self.__target_enabled = target_enabled
        self.__buttons_enabled = buttons_enabled
        self.__source_list.disabled = not source_enabled
        self.__target_list.disabled = not target_enabled
        self.__button_move.disabled = not buttons_enabled
        self.__button_delete.disabled = not buttons_enabled
        self.__update_save_button_state()
        self.__render_target_list()

    def set_source_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(enabled, self.__target_enabled, enabled and self.__target_enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(self.__source_enabled, enabled, self.__source_enabled and enabled)

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__source_items = items
        self.__selected_source_ids.clear()
        self.__source_ids_to_move.clear()
        self.__render_source_list()
        self.__update_save_button_state()

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__target_items = items
        self.__target_item_ids = {item_id for item_id, _ in items}
        self.__initial_target_item_ids = set(self.__target_item_ids)
        self.__selected_target_ids.clear()
        self.__render_target_list()
        self.__update_save_button_state()

    def prepend_target_items(self, items: list[tuple[int, str]], highlight: bool) -> None:
        if not items:
            return
        new_items = [(item_id, label) for item_id, label in items if item_id not in self.__target_item_ids]
        if not new_items:
            return
        self.__target_items = new_items + self.__target_items
        self.__target_item_ids.update(item_id for item_id, _ in new_items)
        if highlight:
            new_ids = [item_id for item_id, _ in new_items]
            self.__source_ids_to_move.update(new_ids)
            self.__selected_target_ids.difference_update(new_ids)
            self.__render_source_list()
        self.__render_target_list()
        self.__update_save_button_state()

    def remove_source_items(self, ids: list[int]) -> None:
        ids_set = set(ids)
        self.__source_items = [(item_id, label) for item_id, label in self.__source_items if item_id not in ids_set]
        self.__selected_source_ids.difference_update(ids_set)
        self.__render_source_list()

    def remove_target_items(self, ids: list[int]) -> None:
        ids_set = set(ids)
        self.__target_items = [(item_id, label) for item_id, label in self.__target_items if item_id not in ids_set]
        self.__target_item_ids.difference_update(ids_set)
        self.__selected_target_ids.difference_update(ids_set)
        self.__source_ids_to_move.difference_update(ids_set)
        self.__render_target_list()
        self.__render_source_list()
        self.__update_save_button_state()

    def get_selected_source_ids(self) -> list[int]:
        return list(self.__selected_source_ids)

    def get_selected_target_ids(self) -> list[int]:
        return list(self.__selected_target_ids)

    def get_source_items_by_ids(self, ids: list[int]) -> list[tuple[int, str]]:
        ids_set = set(ids)
        return [(item_id, label) for item_id, label in self.__source_items if item_id in ids_set]

    def is_target_item_from_source(self, item_id: int) -> bool:
        return item_id in self.__source_ids_to_move

    def has_target_item(self, item_id: int) -> bool:
        return item_id in self.__target_item_ids

    def mark_source_items_as_moved(self, ids: list[int]) -> None:
        if not ids:
            return
        self.__source_ids_to_move.update(ids)
        self.__render_source_list()
        self.__update_save_button_state()

    def get_pending_move_ids(self) -> list[int]:
        return list(self.__source_ids_to_move)

    def __render_source_list(self) -> None:
        controls: list[ft.Control] = []
        for item_id, label in self.__source_items:
            is_selected = item_id in self.__selected_source_ids
            is_moved = item_id in self.__source_ids_to_move
            container = ft.Container(
                content=ft.Text(label, no_wrap=True, color=ft.Colors.ERROR if is_moved else None),
                padding=6,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_selected else None,
            )
            controls.append(
                ft.GestureDetector(
                    content=container,
                    on_tap=lambda _, item_id=item_id: self.__toggle_source_selection(item_id),
                )
            )
        self.__source_list.controls = controls
        self.__safe_update()

    def __render_target_list(self) -> None:
        controls: list[ft.Control] = []
        for item_id, label in self.__target_items:
            is_selected = item_id in self.__selected_target_ids
            is_highlighted = item_id in self.__source_ids_to_move
            if is_highlighted and item_id in self.__initial_target_item_ids:
                text = ft.Column(
                    controls=[
                        ft.Text(label, no_wrap=True, key=f"tgt-txt-{item_id}"),
                        ft.Text(label, no_wrap=True, color=ft.Colors.ERROR),
                    ],
                    spacing=2,
                )
            else:
                text = ft.Text(
                    label, no_wrap=True, color=ft.Colors.ERROR if is_highlighted else None, key=f"tgt-txt-{item_id}"
                )
            container = ft.Container(
                content=text,
                key=f"tgt-row-{item_id}",
                padding=6,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_selected else None,
            )
            selectable = self.__buttons_enabled and (is_highlighted or self.__on_delete_clicked is not None)
            if selectable:
                controls.append(
                    ft.GestureDetector(
                        content=container,
                        on_tap=lambda _, item_id=item_id: self.__toggle_target_selection(item_id),
                    )
                )
            else:
                controls.append(container)
        self.__target_list.controls = controls
        self.__safe_update()

    def __safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            return

    def __toggle_source_selection(self, item_id: int) -> None:
        if item_id in self.__selected_source_ids:
            self.__selected_source_ids.remove(item_id)
        else:
            self.__selected_source_ids.clear()
            self.__selected_source_ids.add(item_id)
        self.__render_source_list()

    def __toggle_target_selection(self, item_id: int) -> None:
        if item_id in self.__selected_target_ids:
            self.__selected_target_ids.remove(item_id)
        else:
            self.__selected_target_ids.clear()
            self.__selected_target_ids.add(item_id)
        self.__render_target_list()

    def __handle_move_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        selected_ids = self.get_selected_source_ids()
        if not selected_ids:
            return
        if self.__on_move_requested:
            self.__on_move_requested(selected_ids)
            return
        self.move_source_items(selected_ids, highlight=True)

    def move_source_items(self, ids_to_add: list[int], highlight: bool) -> None:
        if not ids_to_add:
            return
        existing_ids = [item_id for item_id in ids_to_add if self.has_target_item(item_id)]
        new_ids = [item_id for item_id in ids_to_add if item_id not in existing_ids]
        if existing_ids:
            self.mark_source_items_as_moved(existing_ids)
            self.__render_target_list()
        if not new_ids:
            return
        items_to_move = self.get_source_items_by_ids(new_ids)
        if not items_to_move:
            return
        actual_ids = [item_id for item_id, _ in items_to_move]
        if not actual_ids:
            return
        self.mark_source_items_as_moved(actual_ids)
        self.prepend_target_items(items_to_move, highlight=highlight)

    def __handle_delete_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        selected_ids = self.get_selected_target_ids()
        if not selected_ids:
            return
        moved_ids = [item_id for item_id in selected_ids if self.is_target_item_from_source(item_id)]
        moved_existing_ids = [item_id for item_id in moved_ids if item_id in self.__initial_target_item_ids]
        moved_new_ids = [item_id for item_id in moved_ids if item_id not in moved_existing_ids]
        persisted_ids = [item_id for item_id in selected_ids if item_id not in moved_ids]
        if moved_new_ids:
            self.remove_target_items(moved_new_ids)
        if moved_existing_ids:
            self.__source_ids_to_move.difference_update(moved_existing_ids)
            self.__selected_target_ids.difference_update(moved_existing_ids)
            self.__render_target_list()
        if persisted_ids:
            if self.__on_delete_clicked:
                self.__on_delete_clicked(persisted_ids)
            self.__selected_target_ids.difference_update(persisted_ids)
            self.__render_target_list()

    def __handle_save_clicked(self, event: ft.Event[ft.IconButton]) -> None:
        self.__on_save_clicked(event)

    def __update_save_button_state(self) -> None:
        has_pending = bool(self.__source_ids_to_move)
        self.__button_save.disabled = not (self.__buttons_enabled and has_pending)
