from typing import TypeVar, Generic, TYPE_CHECKING
from views.base import BaseComponent


if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseView(BaseComponent, Generic[TController]):
    def __init__(self, controller: TController, texts: dict[str, str], key: str) -> None:
        super().__init__(controller, texts)
        self._key = key
