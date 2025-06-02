from dataclasses import dataclass, field
from typing import Type
from flet import Control

from views.core import GroupView, UserView


@dataclass
class Views:
    _views: dict[str, Type[Control]] = field(
        default_factory=lambda: {
            "get_users": UserView,
            "create_users": UserView,
            "get_groups": GroupView,
            "create_groups": GroupView,
        }
    )

    def get(self, key: str) -> Type[Control]:
        return self._views[key]
