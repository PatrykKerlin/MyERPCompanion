from collections.abc import Mapping
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Module
from repositories.core import ModuleRepository
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from services.base.base_service import BaseService


class ModuleService(BaseService[Module, ModuleRepository, ModuleStrictSchema, ModulePlainSchema]):
    _repository_cls = ModuleRepository
    _model_cls = Module
    _output_schema_cls = ModulePlainSchema

    async def get_all(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[ModulePlainSchema], int]:
        models = await self._repository_cls.get_all(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls._count_all(session=session, params_filters=filters)
        schemas = [await self.__to_schema(session, model) for model in models]
        return schemas, total

    async def get_one_by_id(self, session: AsyncSession, model_id: int) -> ModulePlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        return await self.__to_schema(session, model)

    async def create(self, session: AsyncSession, created_by: int, schema: ModuleStrictSchema) -> ModulePlainSchema:
        model = self._model_cls(**schema.model_dump(exclude={"groups"}))
        model.created_by = created_by
        saved_model = await self._repository_cls.save(session, model)
        loaded_model = await self._repository_cls.get_one_by_id(session, saved_model.id)
        if not loaded_model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=saved_model.id))
        return await self.__to_schema(session, loaded_model)

    async def update(
        self, session: AsyncSession, model_id: int, modified_by: int, schema: ModuleStrictSchema
    ) -> ModulePlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        for key, value in schema.model_dump(exclude_unset=True, exclude={"groups"}).items():
            setattr(model, key, value)
        model.modified_by = modified_by
        updated_model = await self._repository_cls.save(session, model)
        loaded_model = await self._repository_cls.get_one_by_id(session, updated_model.id)
        if not loaded_model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=updated_model.id))
        return await self.__to_schema(session, loaded_model)

    async def __to_schema(self, session: AsyncSession, model: Module) -> ModulePlainSchema:
        schema = self._output_schema_cls.model_validate(model)
        controllers = await self._repository_cls.get_controller_names(session, model.id)
        return schema.model_copy(update={"controllers": controllers})
