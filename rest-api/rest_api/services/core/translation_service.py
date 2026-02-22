from models.core import Language, Translation
from repositories.core import TranslationRepository
from schemas.core.translation_schema import (
    TranslationByLanguagePlainSchema,
    TranslationPlainSchema,
    TranslationStrictSchema,
)
from services.base.base_service import BaseService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TranslationService(
    BaseService[Translation, TranslationRepository, TranslationStrictSchema, TranslationPlainSchema]
):
    _repository_cls = TranslationRepository
    _model_cls = Translation
    _output_schema_cls = TranslationPlainSchema

    async def get_all_by_language(
        self, session: AsyncSession, language: str, offset: int, limit: int
    ) -> tuple[list[TranslationByLanguagePlainSchema], int]:
        language_id = await session.scalar(select(Language.id).where(Language.symbol == language))
        if language_id is None:
            language_id = await session.scalar(select(Language.id).where(Language.id == 1))
        if language_id is None:
            return [], 0
        models = await self._repository_cls.get_all_by_language_id(session, language_id, offset, limit)
        total = await self._repository_cls.count_all_by_language_id(session, language_id)
        schemas = [TranslationByLanguagePlainSchema.model_validate(model) for model in models]
        return schemas, total
