from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from csv import DictReader
from io import StringIO
from os import getenv
from pathlib import Path
from ast import literal_eval

from aiofiles import open
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import core as mc
from models.base import BaseModel
from schemas import core as sc
from schemas.base import BaseStrictSchema
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
                ("languages", mc.Language, sc.LanguageStrictSchema, {}),
                ("translations", mc.Translation, sc.TranslationStrictSchema, {}),
                ("themes", mc.Theme, sc.ThemeStrictSchema, {}),
                ("groups", mc.Group, sc.GroupStrictSchema, {}),
                ("users", mc.User, sc.UserStrictCreateSchema, {}),
                ("modules", mc.Module, sc.ModuleStrictSchema, {"groups"}),
                ("views", mc.View, sc.ViewStrictSchema, {}),
                ("assoc_users_groups", mc.AssocUserGroup, sc.AssocUserGroupStrictSchema, {}),
                ("assoc_modules_groups", mc.AssocModuleGroup, sc.AssocModuleGroupStrictSchema, {}),
            ]
            for file_name, model_cls, schema_cls, fields_to_exclude in data_to_write:
                file_path = self.__base_path / f"{file_name}.csv"
                await self.__write_new_rows(file_path, model_cls, schema_cls, fields_to_exclude)

    async def update_superuser(self) -> None:
        if self.__superuser:
            async with self.__get_session() as session:
                self.__superuser.language_id = 2
                self.__superuser.theme_id = 1
                self.__superuser.modified_by = self.__superuser.id
                session.add(self.__superuser)
                await session.commit()

    async def __write_new_rows(
        self, file_path: Path, model: type[BaseModel], schema_cls: type[BaseStrictSchema], exclude: set[str]
    ) -> None:
        async with self.__get_session() as session:
            async with open(file_path, mode="r", encoding="utf-8") as file:
                content = await file.read()
                csv_file = StringIO(content)
                reader = DictReader(csv_file)
                for row in reader:
                    for key, value in row.items():
                        if value and value.startswith("[") and value.endswith("]"):
                            try:
                                row[key] = literal_eval(value)
                            except (SyntaxError, ValueError):
                                pass
                        if key == "password" and row[key]:
                            row[key] = Auth.get_password_hash(row[key])
                    validated_row = schema_cls.model_validate(row)
                    instance = model(**validated_row.model_dump(exclude=exclude, exclude_unset=True))
                    instance.created_by = self.__superuser.id if self.__superuser else None
                    session.add(instance)
            await session.commit()

    @staticmethod
    async def __get_model_count(session: AsyncSession, model: type[BaseModel]) -> int:
        result = await session.execute(select(func.count()).select_from(model))
        return result.scalar_one()
