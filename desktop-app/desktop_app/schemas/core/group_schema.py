from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class GroupInputSchema(BaseOutputSchema):
    name: str
    description: str


class GroupOutputSchema(BaseInputSchema):
    name: Annotated[str, Field(min_length=1, max_length=10)]
    description: Annotated[str, Field(min_length=1, max_length=255)]
