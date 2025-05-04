from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class EndpointInputSchema(BaseInputSchema):
    controller: Annotated[str, Field(min_length=1, max_length=50)]
    path: Annotated[str, Field(min_length=1, max_length=25)]
    tag: Annotated[str | None, Field(default=None, min_length=1, max_length=25)]
    module_id: Annotated[int, Field(ge=1)]


class EndpointOutputSchema(BaseOutputSchema):
    controller: str
    path: str
    tag: str | None = None
    module_id: int
