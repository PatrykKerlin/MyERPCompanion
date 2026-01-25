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
    __lock_key = 734982134507

    def __init__(self, get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]], auth: Auth) -> None:
        self.__get_session = get_session
        self.__auth = auth
        self.__superuser: mc.User | None = None
        self.__base_path = Path(__file__).resolve().parent / "initial"

    async def execute(self) -> None:
        async with self.__get_session() as session:
            lock_acquired = await PopulateDatabase.__try_acquire_lock(session)
            if not lock_acquired:
                return
            try:
                await self.__populate_superuser(session)
                await self.__populate_from_sql(session)
                await self.__update_superuser(session)
            except Exception:
                await session.rollback()
                raise
            finally:
                await PopulateDatabase.__release_lock(session)

    async def __populate_superuser(self, session: AsyncSession) -> None:
        username = getenv("SUPERUSER_USERNAME")
        password = getenv("SUPERUSER_PASSWORD")
        if isinstance(username, str) and isinstance(password, str):
            existing_user = await session.scalar(select(mc.User).where(mc.User.username == username))
            if existing_user:
                print("Superuser already exists.")
                return
            hashed_password = await self.__auth.get_password_hash(password)
            superuser = mc.User(username=username, password=hashed_password, is_superuser=True)
            session.add(superuser)
            await session.flush()
            superuser.created_by = superuser.id
            await session.commit()
            self.__superuser = superuser
            print("Superuser created successfully.")

    async def __populate_from_sql(self, session: AsyncSession) -> None:
        if not self.__superuser:
            return

        sql_files = [
            "languages",
            "translations",
            "themes",
            "groups",
            "modules",
            "views",
            "controllers",
            "assoc_view_controllers",
            "assoc_module_groups",
            "currencies",
            "exchange_rates",
            "departments",
            "positions",
            "employees",
            "users",
            "assoc_user_groups",
            "warehouses",
            "bins",
            "units",
            "carriers",
            "delivery_methods",
            "discounts",
            "categories",
            "assoc_category_discounts",
            "suppliers",
            "items",
            "assoc_bin_items",
            "assoc_item_discounts",
            "customers",
            "statuses",
            "assoc_customer_discounts"
        ]
        for file_name in sql_files:
            file_path = self.__base_path / f"{file_name}.sql"
            async with open(file_path, mode="r", encoding="utf-8") as file:
                content = await file.read()
            queries = [query.strip() for query in content.split(";") if query.strip()]
            params: dict[str, int | str] = {"superuser_id": self.__superuser.id}
            if file_name == "users":
                params["password"] = await self.__auth.get_password_hash("test1234")
            for query in queries:
                await session.execute(text(query), params)
            await session.commit()

    async def __update_superuser(self, session: AsyncSession) -> None:
        if self.__superuser:
            self.__superuser.language_id = 2
            self.__superuser.theme_id = 1
            self.__superuser.modified_by = self.__superuser.id
            session.add(self.__superuser)
            await session.commit()

    @staticmethod
    async def __try_acquire_lock(session: AsyncSession) -> bool:
        result = await session.scalar(
            text("SELECT pg_try_advisory_lock(:lock_key)"),
            {"lock_key": PopulateDatabase.__lock_key},
        )
        return bool(result)

    @staticmethod
    async def __release_lock(session: AsyncSession) -> None:
        await session.execute(
            text("SELECT pg_advisory_unlock(:lock_key)"),
            {"lock_key": PopulateDatabase.__lock_key},
        )
