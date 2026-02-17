from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from flet import Page

if TYPE_CHECKING:
    from logging import Logger
    from config.settings import Settings
    from events.event_bus import EventBus
    from states.state_store import StateStore


@dataclass(frozen=True)
class Context:
    page: Page
    settings: Settings
    logger: Logger
    event_bus: EventBus
    state_store: StateStore
