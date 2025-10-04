from __future__ import annotations

from typing import TYPE_CHECKING, Union

from sqlalchemy.exc import NoResultFound

from models.core import View
from repositories.core import ViewRepository
from schemas.core import ViewPlainSchema, ViewStrictSchema
from services.base import BaseService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from utils.auth import Auth


class ViewService(BaseService[View, ViewRepository, ViewStrictSchema, ViewPlainSchema]):
    _repository_cls = ViewRepository
    _model_cls = View
    _output_schema_cls = ViewPlainSchema

    async def get_one_by_key(self, session: AsyncSession, key: str) -> ViewPlainSchema | None:
        model = await self._repository_cls.get_one_by_key(session, key)
        if not model:
            return None
        return self._output_schema_cls.model_validate(model)
