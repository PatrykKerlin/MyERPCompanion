from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import EndpointOutputSchema, GroupOutputSchema


class ModuleInputSchema(BaseInputSchema):
    name: Annotated[str, Field(min_length=1, max_length=25)]
    label: Annotated[str, Field(min_length=1, max_length=25)]
    groups: Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(default=None)]


class ModuleOutputSchema(BaseOutputSchema):
    name: str
    label: str
    endpoints: list[EndpointOutputSchema] = []
    groups: list[GroupOutputSchema] = []
