from typing import Mapping, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business.logistic.item import Item
from models.core.image import Image
from repositories.base.base_repository import BaseRepository
from repositories.mixins.reserved_quantity_mixin import ReservedQuantityMixin


class ItemRepository(ReservedQuantityMixin, BaseRepository[Item]):
    _model_cls = Item

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
            selectinload(cls._model_cls.images),
            with_loader_criteria(Image, cls._expr(Image.is_active.is_(True))),
        )

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[Item]:
        items = await super().get_all(
            session=session,
            offset=offset,
            limit=limit,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        await cls._attach_reserved_quantities(session, items)
        return items

    @classmethod
    async def get_one_by_id(cls, session: AsyncSession, model_id: int) -> Item | None:
        item = await super().get_one_by_id(session, model_id)
        if item:
            await cls._attach_reserved_quantities(session, [item])
        return item

    @classmethod
    async def get_many_by_ids(cls, session: AsyncSession, model_ids: list[int]) -> Sequence[Item]:
        items = await super().get_many_by_ids(session, model_ids)
        await cls._attach_reserved_quantities(session, items)
        return items
