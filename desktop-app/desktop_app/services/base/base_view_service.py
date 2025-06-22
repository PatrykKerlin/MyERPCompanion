from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import PaginatedResponseSchema
from services.base import BaseService

if TYPE_CHECKING:
    from config.context import Context


TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseViewService(BaseService, Generic[TInputSchema]):
    _input_schema_cls: type[TInputSchema]

    def __init__(self, context: Context, endpoint: str) -> None:
        super().__init__(context)
        self._endpoint = endpoint

    async def get_all(
        self, filters: dict[str, str], sort_by: str, order: str, page: int, page_size: int
    ) -> PaginatedResponseSchema[TInputSchema]:
        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "order": order,
            **filters,
        }
        response = await self._get(self._endpoint, params=params)
        data = response.json()
        data["items"] = [self._input_schema_cls(**item) for item in data["items"]]
        return PaginatedResponseSchema[TInputSchema](**data)

    async def get_one(self, id: int) -> TInputSchema:
        response = await self._get(f"{self._endpoint}/{id}")
        return self._input_schema_cls(**response.json())

    async def create(self, schema: BaseOutputSchema) -> TInputSchema:
        payload = schema.model_dump()
        response = await self._post(self._endpoint, payload=payload)
        return self._input_schema_cls(**response.json())

    async def update(self, schema: BaseOutputSchema) -> TInputSchema:
        payload = schema.model_dump()
        response = await self._put(f"{self._endpoint}/{schema.id}", payload=payload)
        return self._input_schema_cls(**response.json())

    async def delete(self, id: int) -> None:
        await self._delete(f"{self._endpoint}/{id}")
