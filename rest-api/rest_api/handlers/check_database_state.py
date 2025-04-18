import asyncio
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from utils.exceptions import DatabaseNotReadyException


class CheckDatabaseState:
    def __init__(
        self,
        get_db: Callable[..., AbstractAsyncContextManager[AsyncSession, bool | None]],
    ) -> None:
        self.__get_db = get_db
        self.__retries = 60
        self.__delay = 1

    async def wait_for_db(self) -> None:
        for attempt in range(1, self.__retries + 1):
            try:
                async with self.__get_db() as db:
                    await db.execute(text("SELECT 1"))
                    print("Database is ready.")
                return
            except OperationalError:
                print(f"Database not ready, attempt {attempt}/{self.__retries}.")
                await asyncio.sleep(self.__delay)
        raise DatabaseNotReadyException()
