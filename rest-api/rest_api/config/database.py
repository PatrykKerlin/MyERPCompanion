from contextlib import asynccontextmanager

from config import Settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database:
    __instance = None
    __base = None

    def __new__(cls, settings: Settings):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, settings: Settings):
        if not hasattr(self, "_initialized"):
            self.engine = create_async_engine(settings.DATABASE_URL, echo=True)
            self.__async_session_local = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            self.__initialized = True

    @classmethod
    def get_base(cls):
        if cls.__base is None:
            cls.__base = declarative_base()
        return cls.__base

    @asynccontextmanager
    async def get_db(self):
        async with self.__async_session_local() as session:
            yield session
