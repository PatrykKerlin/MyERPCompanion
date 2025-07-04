from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseComponent(Generic[TController]):
    def __init__(self, controller: TController, texts: dict[str, str]) -> None:
        self._controller = controller
        self._texts = texts
