from sqlalchemy.ext.asyncio import AsyncSession

from entities.core import Module
from repositories.core import ModuleRepository
from schemas.core import ModuleCreate, ModuleInternal, ModuleResponse
from services.base import BaseService


class ModuleService(
    BaseService[Module, ModuleRepository, ModuleCreate, ModuleResponse]
):
    _repository_cls = ModuleRepository
    _entity_cls = Module
    _response_schema_cls = ModuleResponse

    async def get_internal_by_controller(
        self, session: AsyncSession, controller: str
    ) -> ModuleInternal | None:
        entity = await self._repository_cls.get_by_controller(session, controller)
        if not entity:
            return None
        return ModuleInternal.model_validate(entity)
