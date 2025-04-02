import csv
from pathlib import Path
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from services.base import BaseService
from services import core as services_core
from entities.base import BaseEntity
from entities import core as entities_core
from schemas.base import BaseCreateSchema
from schemas import core as schemas_core

TEntity = TypeVar('TEntity', bound=BaseEntity)
TService = TypeVar("TService", bound=BaseService)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)


class PopulateDatabase(Generic[TEntity, TService, TCreateSchema]):
    def __init__(self, get_db: Callable[..., AbstractAsyncContextManager[AsyncSession, bool | None]]) -> None:
        self.__get_db = get_db
        self.__superuser_id: int | None = None
        self.__base_path = Path(__file__).resolve().parent / "initial_data"

    async def populate_superuser(self) -> None:
        async with self.__get_db() as db:
            count = await self.__get_entity_count(db, entities_core.User)
            if count > 0:
                print("Superuser already exists.")
                return
            username = "admin"
            password = "admin123"
            hashed_password = services_core.AuthService.get_password_hash(password)
            superuser = entities_core.User(
                username=username, password=hashed_password, is_superuser=True
            )
            db.add(superuser)
            await db.commit()
            await db.refresh(superuser)
            self.__superuser_id = superuser.id
            print("Superuser created successfully.")

    async def populate_from_csv(self) -> None:
        data_to_write = [
            ("groups", entities_core.Group, services_core.GroupService, schemas_core.GroupCreate),
        ]
        async with self.__get_db() as db:
            for datum in data_to_write:
                count = await self.__get_entity_count(db, datum[1])
                if count == 0 and self.__superuser_id:
                    file_path = self.__base_path / f"{datum[0]}.csv"
                    await self.__write_new_rows(file_path, datum[2], datum[3])

    async def __write_new_rows(self, file_path: Path, service_cls: type[TService],
                               schema_cls: type[TCreateSchema]) -> None:
        async with self.__get_db() as db:
            with open(file_path) as csv_file:
                reader = csv.DictReader(csv_file)
                service = service_cls()
                for row in reader:
                    schema = schema_cls(**row)
                    await service.create(db, self.__superuser_id, schema=schema)

    @classmethod
    async def __get_entity_count(cls, db: AsyncSession, entity: type[TEntity]) -> int:
        result = await db.execute(select(func.count()).select_from(entity))
        return result.scalar_one()
