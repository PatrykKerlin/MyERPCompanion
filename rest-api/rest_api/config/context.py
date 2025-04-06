from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings


@dataclass
class Context:
    settings: Settings
    get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]
