from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Language, Text
from repositories.core import TextRepository
from schemas.core import TextInputSchema, TextOutputByLanguageSchema, TextOutputSchema
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
    ) -> tuple[list[TextOutputByLanguageSchema], int]:
        filters = [self._model_cls.language.has(Language.key == language)]
        models = await self._repository_cls.get_all(session=session, filters=filters, offset=offset, limit=limit)
        total = await self._repository_cls.count_all(session=session, filters=filters)
        schemas = [TextOutputByLanguageSchema.model_validate(model) for model in models]
        return schemas, total
