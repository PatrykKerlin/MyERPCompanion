from __future__ import annotations
from typing import Callable, TYPE_CHECKING, Any, TypeVar, Generic

from pydantic import BaseModel
from states.base.base_state import BaseState

if TYPE_CHECKING:
    from states.states import AppState

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)
TState = TypeVar("TState", bound=BaseState)


class StateStore(Generic[TBaseModel]):
    def __init__(self, initial: AppState) -> None:
        self.__state: AppState = initial
        self.__listeners: dict[str, list[Callable[[Any], None]]] = {}

    @property
    def app_state(self) -> AppState:
        return self.__state

    def subscribe(self, attr: str, func: Callable[[TState], None]) -> Callable[[], None]:
        def unsubscribe() -> None:
            try:
                self.__listeners[attr].remove(func)
                if not self.__listeners[attr]:
                    del self.__listeners[attr]
            except (ValueError, KeyError):
                pass

        self.__listeners.setdefault(attr, []).append(func)
        return unsubscribe

    def update(self, **attrs: dict[str, Any]) -> None:
        if not attrs:
            return
        updates: dict[str, Any] = {}
        for name, payload in attrs.items():
            current_attr = getattr(self.__state, name)
            new_attr = current_attr.model_copy(update=payload)
            updates[name] = new_attr
        self.__state = self.__state.model_copy(update=updates)
        for name, value in updates.items():
            for func in self.__listeners.get(name, []):
                func(value)
