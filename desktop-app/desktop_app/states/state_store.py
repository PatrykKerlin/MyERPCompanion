from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from states.states import AppState


class StateStore:
    def __init__(self, initial: AppState) -> None:
        self._state: AppState = initial
        self._listeners: list[Callable[[AppState], None]] = []

    def get(self) -> AppState:
        return self._state

    def update(self, mutator: Callable[[AppState], AppState]) -> None:
        self._state = mutator(self._state)
        for listener in list(self._listeners):
            listener(self._state)

    def subscribe(self, func: Callable[[AppState], None]) -> Callable[[], None]:
        def unsubscribe() -> None:
            try:
                self._listeners.remove(func)
            except ValueError:
                pass

        self._listeners.append(func)
        return unsubscribe
