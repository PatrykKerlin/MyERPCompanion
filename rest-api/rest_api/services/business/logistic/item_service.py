from collections.abc import Mapping, Sequence

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.business.logistic.item import Item
from repositories.business.logistic.item_repository import ItemRepository
from repositories.mixins.item_quantity_mixin import ItemQuantityMixin
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.base.base_service import BaseService


class ItemService(BaseService[Item, ItemRepository, ItemStrictSchema, ItemPlainSchema], ItemQuantityMixin):
    _repository_cls = ItemRepository
    _model_cls = Item
    _output_schema_cls = ItemPlainSchema

    async def get_all(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[ItemPlainSchema], int]:
        items = await self._repository_cls.get_all(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls._count_all(session=session, params_filters=filters)
        schemas = await self.__to_schemas(session, items)
        return schemas, total

    async def get_one_by_id(self, session: AsyncSession, model_id: int) -> ItemPlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        return await self.__to_schema(session, model)

    async def get_many_by_ids(self, session: AsyncSession, model_ids: list[int]) -> list[ItemPlainSchema]:
        items = await self._repository_cls.get_many_by_ids(session=session, model_ids=model_ids)
        return await self.__to_schemas(session, items)

    async def create(self, session: AsyncSession, created_by: int, schema: ItemStrictSchema) -> ItemPlainSchema:
        model = self._model_cls(**schema.model_dump())
        model.created_by = created_by
        saved_model = await self._repository_cls.save(session, model)
        return await self.__to_schema(session, saved_model)

    async def update(
        self, session: AsyncSession, model_id: int, modified_by: int, schema: ItemStrictSchema
    ) -> ItemPlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(model, key, value)
        model.modified_by = modified_by
        updated_model = await self._repository_cls.save(session, model)
        return await self.__to_schema(session, updated_model)

    async def __to_schemas(self, session: AsyncSession, items: Sequence[Item]) -> list[ItemPlainSchema]:
        reserved_by_id = await self._get_reserved_quantities(session, items)
        outbound_by_id = await self._get_outbound_quantities(session, items)
        schemas: list[ItemPlainSchema] = []
        for item in items:
            schema = self._output_schema_cls.model_validate(item)
            schemas.append(
                schema.model_copy(
                    update={
                        "reserved_quantity": reserved_by_id.get(item.id, 0),
                        "outbound_quantity": outbound_by_id.get(item.id, 0),
                    }
                )
            )
        return schemas

    async def __to_schema(self, session: AsyncSession, model: Item) -> ItemPlainSchema:
        reserved_by_id = await self._get_reserved_quantities(session, [model])
        outbound_by_id = await self._get_outbound_quantities(session, [model])
        schema = self._output_schema_cls.model_validate(model)
        return schema.model_copy(
            update={
                "reserved_quantity": reserved_by_id.get(model.id, 0),
                "outbound_quantity": outbound_by_id.get(model.id, 0),
            }
        )
