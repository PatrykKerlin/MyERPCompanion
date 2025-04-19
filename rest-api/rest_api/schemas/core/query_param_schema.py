from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from schemas.base import BaseResponseSchema

TResponseSchema = TypeVar("TResponseSchema", bound=BaseResponseSchema)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class FilterParams(BaseModel):
    filters: dict[str, Any] = Field(default={})


class SortingParams(BaseModel):
    sort_by: str | None = Field(default=None)
    order: str = Field(default="asc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel, Generic[TResponseSchema]):
    items: list[TResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
