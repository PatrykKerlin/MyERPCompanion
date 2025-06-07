from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from typing import Generic, TypeVar

from flet import Control

from controllers.base import BaseController
from services.base import BaseService
from schemas.base import BaseOutputSchema

if TYPE_CHECKING:
    from config.context import Context

TService = TypeVar("TService", bound=BaseService)
TView = TypeVar("TView", bound=Control)
TSchema = TypeVar("TSchema", bound=BaseOutputSchema)


class BaseViewController(BaseController[TService], Generic[TService, TView, TSchema], ABC):
    _service_cls: type[TService] | None = None
    _schema_cls: type[TSchema]

    def __init__(self, context: Context) -> None:
        super().__init__(context)

    @abstractmethod
    def view(self, key: str) -> TView:
        pass

    def refresh_page(self) -> None:
        self._context.page.update()
