from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Generic, TypeVar

from controllers.base import BaseController
from services.base import BaseService

if TYPE_CHECKING:
    from config.context import Context

TService = TypeVar("TService", bound=BaseService)


class BaseViewController(BaseController, Generic[TService]):
    _service_cls: type[TService]

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._service = self._service_cls(context)
