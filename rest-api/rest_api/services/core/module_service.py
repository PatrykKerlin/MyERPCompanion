from __future__ import annotations
from typing import TYPE_CHECKING

from models.core import Module, AssocGroupModule
from repositories.core import ModuleRepository, GroupRepository, AssocGroupModuleRepository
from schemas.core import ModulePlainSchema, ModuleStrictSchema
from services.base import BaseService
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ModuleService(BaseService[Module, ModuleRepository, ModuleStrictSchema, ModulePlainSchema]):
    _repository_cls = ModuleRepository
    _model_cls = Module
    _output_schema_cls = ModulePlainSchema

    async def get_by_controller(self, session: AsyncSession, controller: str) -> ModulePlainSchema | None:
        model = await self._repository_cls.get_one_by_controller(session, controller)
        if not model:
            return None
        return ModulePlainSchema.model_validate(model)

    async def create(self, session: AsyncSession, created_by: int, schema: ModuleStrictSchema) -> ModulePlainSchema:
        model = self._model_cls(**schema.model_dump(exclude={"groups"}))
        model.created_by = created_by
        saved_model = await self._repository_cls.save(session, model, False)
        await self._handle_assoc_table(
            session=session,
            assoc_repo_cls=AssocGroupModuleRepository,
            model_cls=AssocGroupModule,
            owner_field="module_id",
            related_field="group_id",
            owner_id=saved_model.id,
            related_ids=schema.groups,
            related_repo_cls=GroupRepository,
            created_by=created_by,
        )
        await session.refresh(saved_model)
        return self._output_schema_cls.model_validate(saved_model)

    async def update(
        self, session: AsyncSession, model_id: int, modified_by: int, schema: ModuleStrictSchema
    ) -> ModulePlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        for key, value in schema.model_dump(exclude_unset=True, exclude={"groups"}).items():
            setattr(model, key, value)
        model.modified_by = modified_by
        updated_model = await self._repository_cls.save(session, model, False)
        await self._handle_assoc_table(
            session=session,
            assoc_repo_cls=AssocGroupModuleRepository,
            model_cls=AssocGroupModule,
            owner_field="module_id",
            related_field="group_id",
            owner_id=updated_model.id,
            related_ids=schema.groups,
            related_repo_cls=GroupRepository,
            created_by=modified_by,
            modified_by=modified_by,
        )
        await session.refresh(updated_model)
        return self._output_schema_cls.model_validate(updated_model)
