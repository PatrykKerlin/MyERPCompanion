from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic

from services.base import BaseService
from schemas.base import BaseInputSchema, BaseOutputSchema

if TYPE_CHECKING:
    from config.context import Context


TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


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
