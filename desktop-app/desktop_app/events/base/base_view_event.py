from dataclasses import dataclass
from events.base.base_event import BaseEvent
from views.base.base_view import BaseView


@dataclass(frozen=True)
class BaseViewRequestedEvent(BaseEvent):
    key: str


@dataclass(frozen=True)
class BaseViewReadyEvent(BaseViewRequestedEvent):
    view: BaseView
