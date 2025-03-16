from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base

from config import Settings


class Database:
    __instance = None
    __base: DeclarativeMeta | None = None

    def __new__(cls, settings: Settings) -> "Database":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, settings: Settings) -> None:
        if not hasattr(self, "_initialized"):
            self.engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True)
            self.__async_session_local = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
            )
            self.__initialized = True

    @classmethod
    def get_base(cls) -> DeclarativeMeta:
        if cls.__base is None:
            cls.__base = declarative_base()
        return cls.__base

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.__async_session_local() as session:
            yield session
