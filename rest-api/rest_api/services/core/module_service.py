from sqlalchemy.ext.asyncio import AsyncSession

from entities.core import Module
from repositories.core import ModuleRepository
from schemas.core import ModuleInputSchema, ModuleOutputSchema
from services.base import BaseService


class ModuleService(BaseService[Module, ModuleRepository, ModuleInputSchema, ModuleOutputSchema]):
    _repository_cls = ModuleRepository
    _entity_cls = Module
    _output_schema_cls = ModuleOutputSchema

    async def get_by_controller(self, session: AsyncSession, controller: str) -> ModuleOutputSchema | None:
        entity = await self._repository_cls.get_by_controller(session, controller)
        if not entity:
            return None
        return ModuleOutputSchema.model_validate(entity)
