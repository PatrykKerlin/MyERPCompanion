from schemas.base import BaseInputSchema, BaseOutputSchema

from .group_schema import GroupInputSchema
from .setting_schema import SettingInputSchema


class UserInputSchema(BaseInputSchema):
    username: str
    language: SettingInputSchema
    theme: SettingInputSchema
    groups: list[GroupInputSchema]
