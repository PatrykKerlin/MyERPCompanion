from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema

from .setting_key_schema import SettingKeyInputSchema


class SettingOutputSchema(BaseInputSchema):
    key_id: Annotated[int, Field(ge=1)]
    value: Annotated[str, Field(min_length=1, max_length=25)]


class SettingInputSchema(BaseOutputSchema):
    key: SettingKeyInputSchema
    value: str
