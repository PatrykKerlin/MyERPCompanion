from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement
from collections.abc import Sequence

from models.core import AssocModuleGroup, Group, Module, View
from repositories.base import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    _model_cls = Module

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.module_groups).selectinload(AssocModuleGroup.group),
            selectinload(cls._model_cls.views),
            with_loader_criteria(Group, cls._expr(Group.is_active == True)),
            with_loader_criteria(View, cls._expr(View.is_active == True)),
        )

    @classmethod
    async def get_all_by_controller(cls, session: AsyncSession, controller: str) -> Sequence[Module]:
        filter_expr = cls._expr(cls._model_cls.views.any(View.controllers.contains([controller])))
        query = cls._build_query([filter_expr])
        result = await session.execute(query)
        return result.scalars().unique().all()
