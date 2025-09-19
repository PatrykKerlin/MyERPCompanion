from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from flet import Page
    from ..events.event_bus import EventBus
    from ..states.state_store import StateStore
    from .settings import Settings


@dataclass(frozen=True)
class Context:
    settings: Settings
    page: Page
    logger: Logger
    event_bus: EventBus
    state_store: StateStore
