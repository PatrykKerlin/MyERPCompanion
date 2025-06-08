from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic

from services.base import BaseService
from schemas.base import BaseInputSchema

if TYPE_CHECKING:
    from config.context import Context


TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)


class BaseViewService(BaseService, Generic[TInputSchema]):
    _input_schema_cls: type[TInputSchema]

    def __init__(self, context: Context, endpoint: str) -> None:
        super().__init__(context)
        self._endpoint = endpoint

    async def get_all(self, filters: dict[str, str] = {}) -> list[TInputSchema]:
        params = {
            "page": 1,
            "page_size": 100,
            "sort_by": "id",
            "order": "asc",
            **filters,
        }
        response = await self._get(self._endpoint, params=params)
        return [self._input_schema_cls(**item) for item in response.json()["items"]]
