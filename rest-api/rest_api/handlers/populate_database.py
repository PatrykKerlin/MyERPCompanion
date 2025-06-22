import csv
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from os import getenv
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import core as mc
from models.base import BaseModel
from schemas import core as sc
from schemas.base import BaseInputSchema
from utils.auth import Auth


class PopulateDatabase:
    def __init__(self, get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        self.__get_session = get_session
        self.__superuser: mc.User | None = None
        self.__base_path = Path(__file__).resolve().parent.parent / "config/initial_data"

    async def populate_superuser(self) -> None:
        async with self.__get_session() as session:
            count = await PopulateDatabase.__get_model_count(session, mc.User)
            if count > 0:
                print("Superuser already exists.")
                return
            username = getenv("SUPERUSER_USERNAME")
            password = getenv("SUPERUSER_PASSWORD")
            if isinstance(username, str) and isinstance(password, str):
                hashed_password = Auth.get_password_hash(password)
                superuser = mc.User(username=username, password=hashed_password, is_superuser=True)
                session.add(superuser)
                await session.flush()
                superuser.created_by = superuser.id
                await session.commit()
                self.__superuser = superuser
                print("Superuser created successfully.")

    async def populate_admins_group(self) -> None:
        if self.__superuser:
            async with self.__get_session() as session:
                key = getenv("ADMINS_GROUP_KEY")
                description = getenv("ADMINS_GROUP_DESC")
                admins = mc.Group(key=key, description=description, created_by=self.__superuser.id)
                session.add(admins)
                await session.commit()

    async def populate_from_csv(self) -> None:
        if self.__superuser:
            data_to_write = [
                ("languages", mc.Language, sc.LanguageInputSchema),
                ("texts", mc.Text, sc.TextInputSchema),
                ("themes", mc.Theme, sc.ThemeInputSchema),
                ("groups", mc.Group, sc.GroupInputSchema),
                ("users", mc.User, sc.UserInputCreateSchema),
                ("users_groups", mc.AssocUserGroup, sc.AssocUserGroupInputSchema),
                ("modules", mc.Module, sc.ModuleInputSchema),
                ("endpoints", mc.Endpoint, sc.EndpointInputSchema),
                ("groups_modules", mc.AssocGroupModule, sc.AssocGroupModuleInputSchema),
            ]
            for file_name, model_cls, schema_cls in data_to_write:
                file_path = self.__base_path / f"{file_name}.csv"
                await self.__write_new_rows(file_path, model_cls, schema_cls)

    async def update_superuser(self) -> None:
        if self.__superuser:
            async with self.__get_session() as session:
                self.__superuser.language_id = 2
                self.__superuser.theme_id = 1
                self.__superuser.modified_by = self.__superuser.id
                session.add(self.__superuser)
                await session.commit()

    async def __write_new_rows(self, file_path: Path, model: type[BaseModel], schema: type[BaseInputSchema]) -> None:
        async with self.__get_session() as session:
            with open(file_path) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if "password" in row.keys() and row["password"]:
                        row["password"] = Auth.get_password_hash(row["password"])
                    validated_row = schema(**row)
                    instance = model(**validated_row.model_dump(exclude_unset=True))
                    instance.created_by = self.__superuser.id if self.__superuser else None
                    session.add(instance)
            await session.commit()

    @staticmethod
    async def __get_model_count(session: AsyncSession, model: type[BaseModel]) -> int:
        result = await session.execute(select(func.count()).select_from(model))
        return result.scalar_one()
