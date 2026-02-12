from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from logging import Logger

from config.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Context:
    settings: Settings
    get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    logger: Logger
