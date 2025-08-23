from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field

from schemas.base import BasePlainSchema

TResponseSchema = TypeVar("TResponseSchema", bound=BasePlainSchema)


class PaginationParamsSchema(BaseModel):
    page: Annotated[int, Field(default=1, ge=1)]
    page_size: Annotated[int, Field(default=10, ge=1, le=100)]


class FilterParamsSchema(BaseModel):
    filters: Annotated[dict[str, Any], Field(default_factory=dict)]


class SortingParamsSchema(BaseModel):
    sort_by: Annotated[str | None, Field(default=None)]
    order: Annotated[str, Field(default="asc", pattern="^(asc|desc)$")]


class PaginatedResponseSchema(BaseModel, Generic[TResponseSchema]):
    items: list[TResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
