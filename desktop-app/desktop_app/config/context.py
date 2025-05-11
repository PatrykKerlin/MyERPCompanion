from asyncio import AbstractEventLoop
from dataclasses import dataclass, field

from config import Controllers, Settings
from schemas.core import TokenSchema, UserSchema


@dataclass
class Context:
    settings: Settings
    loop: AbstractEventLoop
    controllers: Controllers
    texts: dict[str, str] = field(default_factory=dict)
    tokens: TokenSchema | None = None
    user: UserSchema | None = None
