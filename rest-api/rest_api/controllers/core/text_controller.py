from typing import Annotated

from fastapi import Depends, Request, status

from config import Context
from controllers.base import BaseController
from schemas.core import (
    PaginatedResponseSchema,
    PaginationParamsSchema,
    TextInputSchema,
    TextOutputByLanguageSchema,
    TextOutputSchema,
)
from services.core import TextService


class TextController(BaseController[TextService, TextInputSchema, TextOutputSchema]):
    _input_schema_cls: type[TextInputSchema]
    _service_cls = TextService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.router.add_api_route(
            path="/by-language/{language}",
            endpoint=self.texts_by_language,
            methods=["GET"],
            response_model=PaginatedResponseSchema[TextOutputByLanguageSchema],
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(TextOutputSchema)

    async def texts_by_language(
        self, request: Request, language: str, pagination: Annotated[PaginationParamsSchema, Depends()]
    ) -> PaginatedResponseSchema[TextOutputByLanguageSchema]:
        async with self._get_session() as session:
            offset, limit = BaseController._get_offset_and_limit(pagination)
            items, total = await self._service.get_all_by_language(
                session=session, language=language, offset=offset, limit=limit
            )
            has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)

            return PaginatedResponseSchema[TextOutputByLanguageSchema](
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                has_next=has_next,
                has_prev=has_prev,
            )
