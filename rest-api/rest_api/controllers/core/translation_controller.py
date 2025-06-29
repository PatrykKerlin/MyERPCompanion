from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError

from config import Context
from controllers.base import BaseController
from schemas.core import (
    PaginatedResponseSchema,
    PaginationParamsSchema,
    TranslationByLanguagePlainSchema,
    TranslationPlainSchema,
    TranslationStrictSchema,
)
from services.core import TranslationService


class TranslationController(BaseController[TranslationService, TranslationStrictSchema, TranslationPlainSchema]):
    _input_schema_cls: type[TranslationStrictSchema]
    _service_cls = TranslationService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.router.add_api_route(
            path="/by-language/{language}",
            endpoint=self.translations_by_language,
            methods=["GET"],
            response_model=PaginatedResponseSchema[TranslationByLanguagePlainSchema],
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(TranslationPlainSchema)

    async def translations_by_language(
        self, request: Request, language: str, pagination: Annotated[PaginationParamsSchema, Depends()]
    ) -> PaginatedResponseSchema[TranslationByLanguagePlainSchema]:
        try:
            async with self._get_session() as session:
                offset, limit = BaseController._get_offset_and_limit(pagination)
                items, total = await self._service.get_all_by_language(
                    session=session, language=language, offset=offset, limit=limit
                )
                has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)

                return PaginatedResponseSchema[TranslationByLanguagePlainSchema](
                    items=items,
                    total=total,
                    page=pagination.page,
                    page_size=pagination.page_size,
                    has_next=has_next,
                    has_prev=has_prev,
                )
        except HTTPException:
            raise
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
