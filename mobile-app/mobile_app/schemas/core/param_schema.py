from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from schemas.base.base_schema import BaseSchema

TResponseSchema = TypeVar("TResponseSchema", bound=BaseSchema)


class PaginatedResponseSchema(BaseModel, Generic[TResponseSchema]):
    items: list[TResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class IdsPayloadSchema(BaseModel):
    ids: list[int] = Field(default_factory=list)
