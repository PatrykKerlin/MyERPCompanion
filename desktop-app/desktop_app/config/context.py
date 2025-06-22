from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from typing import TYPE_CHECKING

from flet import Page

from schemas.core import ModuleInputSchema, TokenInputSchema, UserInputSchema

if TYPE_CHECKING:
    from settings import Settings

    from config.controllers import Controllers
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
