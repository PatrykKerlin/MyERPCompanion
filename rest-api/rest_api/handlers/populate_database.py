import csv
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from os import getenv
from pathlib import Path
from typing import AsyncGenerator, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from entities import core as ec
from entities.base import BaseEntity
from schemas import core as sc
from schemas.base import BaseCreateSchema
from utils.auth_util import AuthUtil


class PopulateDatabase:
    def __init__(
        self, get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ) -> None:
        self.__get_session = get_session
        self.__superuser_id: int | None = None
        self.__base_path = Path(__file__).resolve().parent.parent / "initial_data"

    async def populate_superuser(self) -> None:
        async with self.__get_session() as session:
            count = await PopulateDatabase.__get_entity_count(session, ec.User)
            if count > 0:
                print("Superuser already exists.")
                return
            username = getenv("SUPERUSER_USERNAME")
            password = getenv("SUPERUSER_PASSWORD")
            if isinstance(username, str) and isinstance(password, str):
                hashed_password = AuthUtil.get_password_hash(password)
                superuser = ec.User(
                    username=username, password=hashed_password, is_superuser=True
                )
                session.add(superuser)
                await session.flush()
                superuser.created_by = superuser.id
                superuser.modified_by = superuser.id
                await session.commit()
                self.__superuser_id = superuser.id
                print("Superuser created successfully.")

    async def populate_admins_group(self) -> None:
        if self.__superuser_id:
            async with self.__get_session() as session:
                name = getenv("ADMINS_GROUP_NAME")
                description = getenv("ADMINS_GROUP_DESC")
                admins = ec.Group(
                    name=name, description=description, created_by=self.__superuser_id
                )
                session.add(admins)
                await session.commit()

    async def populate_from_csv(self) -> None:
        if self.__superuser_id:
            data_to_write = [
                ("groups", ec.Group, sc.GroupCreate),
                ("users", ec.User, sc.UserCreate),
                ("users_groups", ec.AssocUserGroup, sc.AssocUserGroupCreate),
                ("modules", ec.Module, sc.ModuleCreate),
                ("endpoints", ec.Endpoint, sc.EndpointCreate),
                ("groups_modules", ec.AssocGroupModule, sc.AssocGroupModuleCreate),
            ]
            for file_name, entity_cls, schema_cls in data_to_write:
                file_path = self.__base_path / f"{file_name}.csv"
                await self.__write_new_rows(file_path, entity_cls, schema_cls)

    async def __write_new_rows(
        self, file_path: Path, entity: type[BaseEntity], schema: type[BaseCreateSchema]
    ) -> None:
        async with self.__get_session() as session:
            with open(file_path) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if "password" in row.keys() and row["password"]:
                        row["password"] = AuthUtil.get_password_hash(row["password"])
                    validated_row = schema(**row)
                    instance = entity(**validated_row.model_dump(exclude_unset=True))
                    instance.created_by = self.__superuser_id
                    session.add(instance)
            await session.commit()

    @staticmethod
    async def __get_entity_count(
        session: AsyncSession, entity: type[BaseEntity]
    ) -> int:
        result = await session.execute(select(func.count()).select_from(entity))
        return result.scalar_one()
