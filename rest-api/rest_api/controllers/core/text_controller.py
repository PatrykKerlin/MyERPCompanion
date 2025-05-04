from typing import Annotated

from fastapi import Request, status, Depends

from config import Context
from controllers.base import BaseController
from schemas.core import TextInputSchema, TextOutputSchema
from services.core import SettingService, TextService
from utils.validators import SettingsValidator
from schemas.core import PaginatedResponseSchema, PaginationParamsSchema


class TextController(BaseController[TextService, TextInputSchema, TextOutputSchema]):
    _service_cls = TextService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.setting_service = SettingService()
        self.router.add_api_route(
            path="/by-language/{language}",
            endpoint=self.texts_by_language,
            methods=["GET"],
            response_model=TextOutputSchema,
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(TextOutputSchema)

    async def texts_by_language(
        self, request: Request, language: str, pagination: Annotated[PaginationParamsSchema, Depends()]
    ) -> PaginatedResponseSchema[TextOutputSchema]:
        async with self._get_session() as session:
            offset, limit = BaseController._get_offset_and_limit(pagination)
            items, total = await self._service.get_all_by_language(
                session=session, language=language, offset=offset, limit=limit
            )
            has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)

            return PaginatedResponseSchema[TextOutputSchema](
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                has_next=has_next,
                has_prev=has_prev,
            )

    async def _validate_data(self, data: TextInputSchema) -> None:
        async with self._get_session() as session:
            await SettingsValidator.validate_key(session, self.setting_service, data.language_id, "language")
