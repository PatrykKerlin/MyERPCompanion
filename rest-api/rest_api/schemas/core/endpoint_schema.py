from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema, BaseResponseSchema


class EndpointCreate(BaseCreateSchema):
    controller: Annotated[str, Field(min_length=1, max_length=50)]
    path: Annotated[str, Field(min_length=1, max_length=25)]
    tag: Annotated[str, Field(min_length=1, max_length=25)] | None = None
    module_id: Annotated[int, Field(ge=1)]


class EndpointResponse(BaseResponseSchema):
    controller: str
    path: str
    tag: str | None = None
    module_id: int
