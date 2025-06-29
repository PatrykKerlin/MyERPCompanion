from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Module
from repositories.core import ModuleRepository
from schemas.core import ModuleStrictSchema, ModulePlainSchema
from services.base import BaseService


class ModuleService(BaseService[Module, ModuleRepository, ModuleStrictSchema, ModulePlainSchema]):
    _repository_cls = ModuleRepository
    _model_cls = Module
    _output_schema_cls = ModulePlainSchema

    async def get_by_controller(self, session: AsyncSession, controller: str) -> ModulePlainSchema | None:
        model = await self._repository_cls.get_one_by_controller(session, controller)
        if not model:
            return None
        return ModulePlainSchema.model_validate(model)
