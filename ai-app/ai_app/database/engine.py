from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Protocol

from database.base import Base
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class EngineSettings(Protocol):
    DATABASE_URL: str
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int
    DB_POOL_PRE_PING: bool


class Engine:
    __instance = None
    __initialized: bool = False
    __base = Base

    def __new__(cls, _: EngineSettings) -> Engine:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, settings: EngineSettings) -> None:
        if not self.__initialized:
            self.engine: AsyncEngine = create_async_engine(
                settings.DATABASE_URL,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=settings.DB_POOL_PRE_PING,
            )
            self.__async_session_maker = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
            )
            self.__initialized = True

    @classmethod
    def get_base(cls) -> type[Base]:
        return cls.__base

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.__async_session_maker() as session:
            yield session
