from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class GroupInputSchema(BaseInputSchema):
    name: Annotated[str, Field(min_length=1, max_length=10)]
    description: Annotated[str, Field(min_length=1, max_length=255)]


class GroupOutputSchema(BaseOutputSchema):
    name: str
    description: str
