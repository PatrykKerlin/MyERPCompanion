import flet as ft
from typing import Callable


class DualAssign(ft.Container):
    def __init__(
        self,
        source_label: str,
        target_label: str,
        on_source_submitted: Callable[[ft.ControlEvent], None],
        on_target_submitted: Callable[[ft.ControlEvent], None],
        on_row_clicked: Callable[[], None],
    ) -> None:
        super().__init__(expand=True)
        self.__source_enabled = False
        self.__target_enabled = False

        self.__source_items = []
        self.__target_items = []
        self.__selected_source_ids = set()
        self.__source_ids_to_move: set[int] = set()

        self.__on_row_clicked = on_row_clicked

        self.__source_input = ft.TextField(label=source_label, on_submit=on_source_submitted)
        self.__target_input = ft.TextField(label=target_label, on_submit=on_target_submitted)

        self.__source_list = ft.ListView(expand=True, spacing=2, auto_scroll=False, disabled=True)
        self.__target_list = ft.ListView(expand=True, spacing=2, auto_scroll=False, disabled=True)

        self.__button_move = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD, disabled=True, on_click=self.__handle_row_clicked
        )
        self.__button_delete = ft.IconButton(icon=ft.Icons.DELETE, disabled=True)
        self.__button_save = ft.IconButton(icon=ft.Icons.SAVE, disabled=True)

        source_header = ft.Row(
            controls=[
                ft.Container(content=self.__source_input, expand=1),
                ft.Container(expand=1),
            ],
            spacing=8,
        )
        target_header = ft.Row(
            controls=[
                ft.Container(content=self.__target_input, expand=1),
                ft.Container(expand=1),
            ],
            spacing=8,
        )

        source_column = ft.Column(
            controls=[
                source_header,
                ft.Container(
                    content=self.__source_list,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
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
                target_header,
                ft.Container(
                    content=self.__target_list,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
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

    def set_enabled_states(self, source_enabled: bool, target_enabled: bool, buttons_enabled: bool) -> None:
        self.__source_enabled = source_enabled
        self.__target_enabled = target_enabled
        self.__source_list.disabled = not source_enabled
        self.__target_list.disabled = not target_enabled
        self.__button_move.disabled = not buttons_enabled
        self.__button_delete.disabled = not buttons_enabled
        self.__button_save.disabled = not buttons_enabled
        self.update()

    def set_source_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(enabled, self.__target_enabled, enabled and self.__target_enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.set_enabled_states(self.__source_enabled, enabled, self.__source_enabled and enabled)

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__source_items = items
        self.__selected_source_ids.clear()
        self.__render_source_list()

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__target_items = items
        self.__render_target_list()

    def prepend_target_items(self, items: list[tuple[int, str]], highlight: bool) -> None:
        self.__target_items = items + self.__target_items
        if highlight:
            self.__source_ids_to_move.update(i for i, _ in items)
        self.__render_target_list()

    def remove_source_items(self, ids: list[int]) -> None:
        ids_set = set(ids)
        self.__source_items = [(i, v) for i, v in self.__source_items if i not in ids_set]
        self.__selected_source_ids.difference_update(ids_set)
        self.__render_source_list()

    def get_selected_source_ids(self) -> list[int]:
        return list(self.__selected_source_ids)

    def set_source_error(self, message: str | None) -> None:
        self.__source_input.error_text = message
        self.update()

    def set_target_error(self, message: str | None) -> None:
        self.__target_input.error_text = message
        self.update()

    def __render_source_list(self) -> None:
        controls: list[ft.Control] = []
        for item_id, label in self.__source_items:
            is_selected = item_id in self.__selected_source_ids
            container = ft.Container(
                content=ft.Text(label, no_wrap=True),
                padding=6,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_selected else None,
            )
            gd = ft.GestureDetector(
                content=container,
                on_tap=lambda e, iid=item_id: self.__toggle_source_selection(iid),
            )
            controls.append(gd)
        self.__source_list.controls = controls
        self.update()

    def __render_target_list(self) -> None:
        controls: list[ft.Control] = []
        for item_id, label in self.__target_items:
            is_highlighted = item_id in self.__source_ids_to_move
            text = ft.Text(
                label, no_wrap=True, color=ft.Colors.ERROR if is_highlighted else None, key=f"tgt-txt-{item_id}"
            )
            controls.append(ft.Container(content=text, key=f"tgt-row-{item_id}"))
        self.__target_list.controls = controls
        self.update()

    def __toggle_source_selection(self, item_id: int) -> None:
        if item_id in self.__selected_source_ids:
            self.__selected_source_ids.remove(item_id)
        else:
            self.__selected_source_ids.add(item_id)
        self.__render_source_list()

    def __handle_row_clicked(self, _: ft.ControlEvent) -> None:
        if self.__on_row_clicked:
            self.__on_row_clicked()
