from dataclasses import dataclass
from flet import Page
from config import Controllers, Settings
from schemas.core import TokenInputSchema, UserInputSchema


@dataclass
class Context:
    settings: Settings
    controllers: Controllers
    page: Page
    texts: dict[str, str]
    tokens: TokenInputSchema | None = None
    user: UserInputSchema | None = None
