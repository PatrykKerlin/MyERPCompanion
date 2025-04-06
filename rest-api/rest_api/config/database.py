from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import Base, Settings


class Database:
    __instance = None
    __initialized: bool = False
    __base = Base

    def __new__(cls, settings: Settings) -> "Database":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, settings: Settings) -> None:
        if not self.__initialized:
            self.engine: AsyncEngine = create_async_engine(
                settings.DATABASE_URL,
                echo=True,
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
