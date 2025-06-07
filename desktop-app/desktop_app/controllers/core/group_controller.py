from __future__ import annotations
from typing import TYPE_CHECKING, Any

from controllers.base import BaseViewController
from services.core import GroupService
from views.core import GroupView
from schemas.core import GroupOutputSchema
import flet as ft
from pydantic import ValidationError
from views.components import LoadingDialogComponent

if TYPE_CHECKING:
    from config.context import Context


class GroupController(BaseViewController[GroupService, GroupView, GroupOutputSchema]):
    _schema_cls = GroupOutputSchema
    _service_cls = GroupService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__view: GroupView | None = None
        self.__search_fields: set[str] = set()
        self.__field_values: dict[str, str] = {}

    def view(self, key: str) -> GroupView:
        if key == "get_groups":
            self.__view = GroupView(self, self._context.texts)
            return self.__view
        raise ValueError("Requested view not found.")

    def get_constraint(self, field: str, constraint: str) -> Any:
        metadata = self._schema_cls.model_fields[field].metadata
        for item in metadata:
            if hasattr(item, constraint):
                return getattr(item, constraint)
        return None

    def toggle_search_marker(self, field: str, is_marked: bool) -> None:
        if is_marked:
            self.__search_fields.add(field)
            error = self.__validate_field(field, self.__field_values.get(field, ""))
            if self.__view:
                self.__view.set_field_error(field, error)
        else:
            self.__search_fields.discard(field)
            if self.__view:
                self.__view.set_field_error(field, None)

    def set_field_value(self, field: str, value: str) -> None:
        self.__field_values[field] = value
        if field in self.__search_fields:
            error = self.__validate_field(field, value)
            if self.__view:
                self.__view.set_field_error(field, error)

    def on_search_click(self, _: ft.ControlEvent) -> None:
        self._context.page.run_task(self.__perform_search)

    def __validate_field(self, field: str, value: Any) -> str | None:
        try:
            self._schema_cls(**{field: value})
        except ValidationError as err:
            for e in err.errors():
                if e["loc"] == (field,):
                    return e["msg"]
        return None

    async def __perform_search(self) -> None:
        filters: dict[str, str] = {}
        loading_dialog = LoadingDialogComponent(self._context.texts)
        self._open_dialog(loading_dialog)
        for field in self.__search_fields:
            filters[field] = self.__field_values.get(field, "").strip()
        results = await self._service.get_all_groups(filters=filters)
        self._close_dialog(loading_dialog)
        if self.__view:
            self.__view.replace_content([result.model_dump() for result in results])
