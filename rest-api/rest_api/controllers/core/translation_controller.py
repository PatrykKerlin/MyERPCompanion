from typing import Annotated

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Depends, Request, status
from schemas.core.param_schema import PaginatedResponseSchema, PaginationParamsSchema
from schemas.core.translation_schema import (
    TranslationByLanguagePlainSchema,
    TranslationPlainSchema,
    TranslationStrictSchema,
)
from services.core import TranslationService
from utils.auth import Auth


class TranslationController(BaseController[TranslationService, TranslationStrictSchema, TranslationPlainSchema]):
    _input_schema_cls = TranslationStrictSchema
    _service_cls = TranslationService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self.router.add_api_route(
            path="/by-language/{language}",
            endpoint=self.get_all_by_language,
            methods=["GET"],
            response_model=PaginatedResponseSchema[TranslationByLanguagePlainSchema],
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(TranslationPlainSchema)

    @BaseController.handle_exceptions()
    async def get_all_by_language(
        self, request: Request, language: str, pagination: Annotated[PaginationParamsSchema, Depends()]
    ) -> PaginatedResponseSchema[TranslationByLanguagePlainSchema]:
        session = BaseController._get_request_session(request)
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
