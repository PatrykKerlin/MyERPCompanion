from typing import Generic, TypeVar

from pydantic import BaseModel

from schemas.base import BaseInputSchema

TResponseSchema = TypeVar("TResponseSchema", bound=BaseInputSchema)


class PaginatedResponseSchema(BaseModel, Generic[TResponseSchema]):
    items: list[TResponseSchema]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
