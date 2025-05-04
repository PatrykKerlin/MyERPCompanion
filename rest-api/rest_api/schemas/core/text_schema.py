from typing import Annotated
from datetime import datetime

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import SettingOutputSchema


class TextInputSchema(BaseInputSchema):
    name: Annotated[str, Field(min_length=1, max_length=25)]
    value: Annotated[str, Field(min_length=1, max_length=255)]
    language_id: Annotated[int, Field(ge=1)]


class TextOutputSchema(BaseOutputSchema):
    name: str
    value: str
    language: SettingOutputSchema


class TextOutputByLanguageSchema(BaseOutputSchema):
    name: str
    value: str
    is_active: Annotated[bool, Field(exclude=True)]
    created_at: Annotated[datetime, Field(exclude=True)]
    created_by: Annotated[int, Field(exclude=True)]
    modified_at: Annotated[datetime | None, Field(exclude=True)] = None
    modified_by: Annotated[int | None, Field(exclude=True)] = None
