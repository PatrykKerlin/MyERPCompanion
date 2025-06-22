from __future__ import annotations
from typing import TYPE_CHECKING
from logging import Logger

from dataclasses import dataclass, field

from flet import Page


from schemas.core import TokenInputSchema, UserInputSchema, ModuleInputSchema

if TYPE_CHECKING:
    from controllers import Controllers
    from settings import Settings
    from views.base.base_view import BaseView


@dataclass
class Context:
    settings: Settings
    page: Page
    texts: dict[str, str]
    logger: Logger
    tokens: TokenInputSchema | None = None
    user: UserInputSchema = field(init=False)
    controllers: Controllers = field(init=False)
    modules: list[ModuleInputSchema] = field(default_factory=list)
    active_views: dict[str, BaseView] = field(default_factory=dict)
