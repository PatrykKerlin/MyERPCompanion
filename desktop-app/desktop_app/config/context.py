from dataclasses import dataclass
from flet import Page
from config import Controllers, Settings
from schemas.core import TokenSchema, UserSchema


@dataclass
class Context:
    settings: Settings
    controllers: Controllers
    page: Page
    texts: dict[str, str]
    tokens: TokenSchema | None = None
    user: UserSchema | None = None
