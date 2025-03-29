from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import AsyncContextManager
from collections.abc import Callable

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings


@dataclass
class Context:
    get_db: Callable[..., AbstractAsyncContextManager[AsyncSession, bool | None]]
    settings: Settings
    oauth2_scheme: OAuth2PasswordBearer
