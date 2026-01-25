from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import AssocModuleGroup, AssocViewController, Controller, Group, Module, View
from repositories.base.base_repository import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    _model_cls = Module

    @classmethod
    def _build_query(
        cls,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(params_filters, additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.module_groups).selectinload(AssocModuleGroup.group),
            selectinload(cls._model_cls.views)
            .selectinload(View.view_controllers)
            .selectinload(AssocViewController.controller),
            with_loader_criteria(AssocModuleGroup, cls._expr(AssocModuleGroup.is_active.is_(True))),
            with_loader_criteria(AssocViewController, cls._expr(AssocViewController.is_active.is_(True))),
            with_loader_criteria(Controller, cls._expr(Controller.is_active.is_(True))),
            with_loader_criteria(Group, cls._expr(Group.is_active.is_(True))),
            with_loader_criteria(View, cls._expr(View.is_active.is_(True))),
        )

    @classmethod
    async def get_controller_names(cls, session: AsyncSession, module_id: int) -> list[str]:
        result = await session.execute(
            select(Controller.name)
            .distinct()
            .join(AssocViewController, AssocViewController.controller_id == Controller.id)
            .join(View, View.id == AssocViewController.view_id)
            .where(
                Controller.is_active.is_(True),
                AssocViewController.is_active.is_(True),
                View.is_active.is_(True),
                View.module_id == module_id,
            )
        )
        return sorted(result.scalars().all())
