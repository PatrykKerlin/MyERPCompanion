from typing import TYPE_CHECKING, Generic, TypeVar

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.base.base_service import BaseService

if TYPE_CHECKING:
    from utils.enums import Endpoint


TInputSchema = TypeVar("TInputSchema", bound=BasePlainSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseStrictSchema)


class BaseViewService(BaseService, Generic[TInputSchema]):
    _input_schema_cls: type[TInputSchema]

    # async def get_all(
    #     self, endpoint: Endpoint, filters: dict[str, str], sort_by: str, order: str, page: int, page_size: int
    # ) -> PaginatedResponseSchema[TInputSchema]:
    #     params = {
    #         "page": page,
    #         "page_size": page_size,
    #         "sort_by": sort_by,
    #         "order": order,
    #         **filters,
    #     }
    #     response = await self._get(endpoint, query_params=params)
    #     data = response.json()
    #     data["items"] = [self._input_schema_cls(**item) for item in data["items"]]
    #     return PaginatedResponseSchema[TInputSchema](**data)

    # async def get_one(self, endpoint: Endpoint, id: int) -> TInputSchema:
    #     response = await self._get(f"{endpoint}/{id}")
    #     return self._input_schema_cls(**response.json())

    # async def create(self, endpoint: Endpoint, schema: BaseStrictSchema) -> TInputSchema:
    #     payload = schema.model_dump()
    #     response = await self._post(endpoint, body_params=payload)
    #     return self._input_schema_cls(**response.json())

    # async def update(self, endpoint: Endpoint, schema: BaseStrictSchema) -> TInputSchema:
    #     payload = schema.model_dump()
    #     response = await self._put(f"{endpoint}/{schema.id}", body_params=payload)
    #     return self._input_schema_cls(**response.json())

    # async def delete(self, endpoint: Endpoint, id: int) -> None:
    #     await self._delete(f"{endpoint}/{id}")
