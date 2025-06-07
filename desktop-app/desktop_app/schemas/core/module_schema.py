from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import EndpointInputSchema, GroupInputSchema


class ModuleInputSchema(BaseInputSchema):
    key: str
    order: int
    endpoints: list[EndpointInputSchema] = []
    groups: list[GroupInputSchema] = []


class ModuleOutputSchema(BaseOutputSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    order: Annotated[int, Field(ge=1)]
    groups: Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(default=None)]
