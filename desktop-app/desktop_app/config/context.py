from asyncio import AbstractEventLoop
from dataclasses import dataclass

from config import Controllers, Settings
from schemas.core import TokenSchema, UserSchema


@dataclass
class Context:
    settings: Settings
    loop: AbstractEventLoop
    controllers: Controllers
    language: str
    tokens: TokenSchema | None = None
    user: UserSchema | None = None
