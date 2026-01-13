from collections.abc import Mapping
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import AssocModuleGroup, Group, Module, View
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
            selectinload(cls._model_cls.views),
            with_loader_criteria(AssocModuleGroup, cls._expr(AssocModuleGroup.is_active.is_(True))),
            with_loader_criteria(Group, cls._expr(Group.is_active.is_(True))),
            with_loader_criteria(View, cls._expr(View.is_active.is_(True))),
        )
