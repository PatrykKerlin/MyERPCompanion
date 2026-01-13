from typing import Mapping
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business.hr import Department, Employee, Position
from models.core import User
from repositories.base.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    _model_cls = Employee

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
            selectinload(cls._model_cls.department),
            selectinload(cls._model_cls.position),
            selectinload(cls._model_cls.user),
            selectinload(cls._model_cls.manager),
            selectinload(cls._model_cls.subordinates),
            with_loader_criteria(Department, cls._expr(Department.is_active.is_(True))),
            with_loader_criteria(Position, cls._expr(Position.is_active.is_(True))),
            with_loader_criteria(User, cls._expr(User.is_active.is_(True))),
        )
