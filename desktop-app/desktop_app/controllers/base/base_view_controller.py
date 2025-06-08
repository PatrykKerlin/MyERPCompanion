from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from typing import Generic, TypeVar

from flet import Control

from controllers.base import BaseController
from services.base import BaseViewService
from schemas.base import BaseOutputSchema

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.endpoint_schema import EndpointInputSchema

TService = TypeVar("TService", bound=BaseViewService)
TView = TypeVar("TView", bound=Control)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseViewController(BaseController, Generic[TService, TView, TOutputSchema], ABC):
    _service_cls: type[TService]
    _output_schema_cls: type[TOutputSchema]

    def __init__(self, context: Context, endpoint: EndpointInputSchema) -> None:
        super().__init__(context)
        self._service = self._service_cls(context, endpoint.path)
        self._endpoint = endpoint

    @abstractmethod
    def view(self, key: str, row: dict[str, Any] | None = None) -> TView:
        pass

    def refresh_page(self) -> None:
        self._context.page.update()

    def on_row_click(self, key: str, row: dict[str, Any]) -> None:
        new_key = f"{key}_{row["id"]}"
        if new_key not in self._context.active_views.keys():
            controller = self._context.controllers.get_view_controller(key)
            view = controller.view(key, row)
            self._context.active_views[new_key] = view
        view = self._context.active_views[new_key]
        tabs_bar_controller = self._context.controllers.get("tabs_bar")
        tabs_bar_controller.add_tab(new_key)
        app_controller = self._context.controllers.get("app")
        app_controller.render_view(view)
