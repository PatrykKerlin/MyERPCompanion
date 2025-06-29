from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Language, Translation
from repositories.core import TranslationRepository
from schemas.core import TranslationStrictSchema, TranslationByLanguagePlainSchema, TranslationPlainSchema
from services.base import BaseService


class TranslationService(
    BaseService[Translation, TranslationRepository, TranslationStrictSchema, TranslationPlainSchema]
):
    _repository_cls = TranslationRepository
    _model_cls = Translation
    _output_schema_cls = TranslationPlainSchema

    async def get_all_by_language(
        self,
        session: AsyncSession,
        language: str,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[TranslationByLanguagePlainSchema], int]:
        filters = [self._model_cls.language.has(Language.key == language)]
        models = await self._repository_cls.get_all(session=session, filters=filters, offset=offset, limit=limit)
        total = await self._repository_cls.count_all(session=session, filters=filters)
        schemas = [TranslationByLanguagePlainSchema.model_validate(model) for model in models]
        return schemas, total
