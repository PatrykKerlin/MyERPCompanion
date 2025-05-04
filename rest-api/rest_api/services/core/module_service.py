from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Module
from repositories.core import ModuleRepository
from schemas.core import ModuleInputSchema, ModuleOutputSchema
from services.base import BaseService


class ModuleService(BaseService[Module, ModuleRepository, ModuleInputSchema, ModuleOutputSchema]):
    _repository_cls = ModuleRepository
    _model_cls = Module
    _output_schema_cls = ModuleOutputSchema

    async def get_by_controller(self, session: AsyncSession, controller: str) -> ModuleOutputSchema | None:
        model = await self._repository_cls.get_one_by_controller(session, controller)
        if not model:
            return None
        return ModuleOutputSchema.model_validate(model)
