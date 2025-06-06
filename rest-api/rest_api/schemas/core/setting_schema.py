from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import SettingKeyOutputSchema


class SettingInputSchema(BaseInputSchema):
    key_id: Annotated[int, Field(ge=1)]
    value: Annotated[str, Field(min_length=1, max_length=25)]


class SettingOutputSchema(BaseOutputSchema):
    key: SettingKeyOutputSchema
    value: str
