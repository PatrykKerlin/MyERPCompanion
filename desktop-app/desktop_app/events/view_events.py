from dataclasses import dataclass

from events.base.base_view_event import BaseViewReadyEvent, BaseViewRequestedEvent


@dataclass(frozen=True)
class ViewReady(BaseViewReadyEvent):
    pass


@dataclass(frozen=True)
class GroupViewRequested(BaseViewRequestedEvent):
    pass
