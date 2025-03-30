from pathlib import Path
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from entities.core import User


class PopulateDB:
    def __init__(self, get_db: Callable[..., AbstractAsyncContextManager[AsyncSession, bool | None]]) -> None:
        self.__get_db = get_db

    async def populate_from_sql(self) -> None:
        async with self.__get_db() as db:
            count = await self.__get_user_count(db)
            if count > 0:
                print("Users already exist. Skipping SQL initialization.")
                return
            await self.__run_sql_file(db)
            print("SQL initialization complete.")

    @classmethod
    async def __get_user_count(cls, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    @classmethod
    async def __run_sql_file(cls, db: AsyncSession) -> None:
        file_path = Path(__file__).resolve().parent.parent / "initial.sql"
        if not file_path.exists():
            print(f"File {file_path} does not exist!")
            return

        sql_queries = file_path.read_text()
        try:
            for query in filter(None, sql_queries.split(";")):
                query = query.strip()
                if query:
                    await db.execute(text(query))
                    await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Error: {e}")
