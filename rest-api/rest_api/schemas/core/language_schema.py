from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class LanguageInputSchema(BaseInputSchema):
    key: Annotated[str, Field(min_length=2, max_length=2)]


class LanguageOutputSchema(BaseOutputSchema):
    key: str
