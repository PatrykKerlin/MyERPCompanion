from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from entities.core import Endpoint, Group, Module
from repositories.base import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    _model_cls = Module

    @classmethod
    def _build_query(
        cls, additional_filters: list[ColumnElement[bool]] | None = None
    ) -> Select:
        query = super()._build_query(additional_filters)
        return query.options(
            selectinload(Module.groups),
            selectinload(Module.endpoints),
            with_loader_criteria(Group, cls._expr(Group.is_active == True)),
            with_loader_criteria(Endpoint, cls._expr(Endpoint.is_active == True)),
        )

    @classmethod
    async def get_by_controller(
        cls, session: AsyncSession, controller: str
    ) -> Module | None:
        query = cls._build_query([cls._expr(Endpoint.controller == controller)])
        result = await session.execute(query)
        return result.scalars().first()
