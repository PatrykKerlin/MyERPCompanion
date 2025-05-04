from typing import Any, TypeVar, Union, cast

from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Text, Setting, SettingKey
from repositories.core import TextRepository
from schemas.core import TextInputSchema, TextOutputSchema
from services.base import BaseService


class TextService(BaseService[Text, TextRepository, TextInputSchema, TextOutputSchema]):
    _repository_cls = TextRepository
    _model_cls = Text
    _output_schema_cls = TextOutputSchema

    async def get_all_by_language(
        self,
        session: AsyncSession,
        language: str,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[TextOutputSchema], int]:
        filters = [
            Text.language.has(Setting.key.has(SettingKey.key == "language")),
            Text.language.has(Setting.value == language),
        ]
        models = await self._repository_cls.get_all(session=session, filters=filters, offset=offset, limit=limit)
        total = await self._repository_cls.count_all(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(model) for model in models]
        return schemas, total
