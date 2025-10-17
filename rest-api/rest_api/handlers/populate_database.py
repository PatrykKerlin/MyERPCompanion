from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from os import getenv
from pathlib import Path

from aiofiles import open
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models import core as mc
from models.base.base_model import BaseModel
from utils.auth import Auth


class PopulateDatabase:
    def __init__(self, get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]], auth: Auth) -> None:
        self.__get_session = get_session
        self.__auth = auth
        self.__superuser: mc.User | None = None
        self.__base_path = Path(__file__).resolve().parent.parent / "config/initial_data"

    async def execute(self) -> None:
        await self.__populate_superuser()
        await self.__populate_from_sql()
        await self.__update_superuser()

    async def __populate_superuser(self) -> None:
        async with self.__get_session() as session:
            count = await PopulateDatabase.__get_model_count(session, mc.User)
            if count > 0:
                print("Superuser already exists.")
                return
            username = getenv("SUPERUSER_USERNAME")
            password = getenv("SUPERUSER_PASSWORD")
            if isinstance(username, str) and isinstance(password, str):
                hashed_password = self.__auth.get_password_hash(password)
                superuser = mc.User(username=username, password=hashed_password, is_superuser=True)
                session.add(superuser)
                await session.flush()
                superuser.created_by = superuser.id
                await session.commit()
                self.__superuser = superuser
                print("Superuser created successfully.")

    async def __populate_from_sql(self) -> None:
        if not self.__superuser:
            return

        sql_files = [
            "languages",
            "translations",
            "themes",
            "groups",
            "modules",
            "views",
            "assoc_module_groups",
            "currencies",
            "departments",
            "positions",
            "employees",
            "users",
            "assoc_user_groups",
            "assoc_user_views",
        ]
        for file_name in sql_files:
            file_path = self.__base_path / f"{file_name}.sql"
            async with self.__get_session() as session:
                async with open(file_path, mode="r", encoding="utf-8") as file:
                    content = await file.read()
                queries = [query.strip() for query in content.split(";") if query.strip()]
                params: dict[str, int | str] = {"superuser_id": self.__superuser.id}
                if file_name == "users":
                    params["password"] = self.__auth.get_password_hash("test1234")
                for query in queries:
                    await session.execute(text(query), params)
                await session.commit()

    async def __update_superuser(self) -> None:
        if self.__superuser:
            async with self.__get_session() as session:
                self.__superuser.language_id = 2
                self.__superuser.theme_id = 1
                self.__superuser.modified_by = self.__superuser.id
                session.add(self.__superuser)
                await session.commit()

    @staticmethod
    async def __get_model_count(session: AsyncSession, model: type[BaseModel]) -> int:
        result = await session.execute(select(func.count()).select_from(model))
        return result.scalar_one()
