from pydantic import Field

from schemas.base import BaseCreateSchema, BaseResponseSchema


class EndpointCreate(BaseCreateSchema):
    controller: str = Field(min_length=1, max_length=50)
    path: str = Field(min_length=1, max_length=25)
    tag: str | None = Field(default=None, min_length=1, max_length=25)
    module_id: int = Field(ge=1)


class EndpointResponse(BaseResponseSchema):
    controller: str
    path: str
    tag: str | None = None
    module_id: int
