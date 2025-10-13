from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from config.settings import Settings
    from events.event_bus import EventBus
    from flet import Page
    from logging import Logger
    from states.state_store import StateStore


@dataclass(frozen=True)
class Context:
    settings: Settings
    page: Page
    logger: Logger
    event_bus: EventBus
    state_store: StateStore
