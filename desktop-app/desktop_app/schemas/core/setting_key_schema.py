from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class SettingKeyInputSchema(BaseOutputSchema):
    key: str


class SettingKeyOutputSchema(BaseInputSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
