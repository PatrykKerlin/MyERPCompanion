from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class EndpointInputSchema(BaseInputSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    controller: Annotated[str, Field(min_length=1, max_length=50)]
    path: Annotated[str, Field(min_length=1, max_length=100)]
    in_menu: bool
    order: Annotated[int, Field(ge=1)]
    module_id: Annotated[int, Field(ge=1)]


class EndpointOutputSchema(BaseOutputSchema):
    key: str
    controller: str
    path: str
    in_menu: bool
    order: int
