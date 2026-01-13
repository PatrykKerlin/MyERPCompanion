from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Translation
from repositories.core import TranslationRepository
from schemas.core.translation_schema import (
    TranslationByLanguagePlainSchema,
    TranslationPlainSchema,
    TranslationStrictSchema,
)
from services.base.base_service import BaseService


class TranslationService(
    BaseService[Translation, TranslationRepository, TranslationStrictSchema, TranslationPlainSchema]
):
    _repository_cls = TranslationRepository
    _model_cls = Translation
    _output_schema_cls = TranslationPlainSchema

    async def get_all_by_language(
        self, session: AsyncSession, language: str, offset: int, limit: int
    ) -> tuple[list[TranslationByLanguagePlainSchema], int]:
        models = await self._repository_cls.get_all_by_language(session, language, offset, limit)
        total = await self._repository_cls.count_all_by_language(session, language)
        schemas = [TranslationByLanguagePlainSchema.model_validate(model) for model in models]
        return schemas, total
