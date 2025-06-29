from datetime import datetime
from typing import Annotated

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.core import LanguagePlainSchema


class TranslationStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    value: Annotated[str, Field(min_length=1, max_length=255)]
    language_id: Annotated[int, Field(ge=1)]


class TranslationPlainSchema(BasePlainSchema):
    key: str
    value: str
    language: LanguagePlainSchema


class TranslationByLanguagePlainSchema(BasePlainSchema):
    key: str
    value: str
    is_active: Annotated[bool, Field(exclude=True)]
    created_at: Annotated[datetime, Field(exclude=True)]
    created_by: Annotated[int, Field(exclude=True)]
    modified_at: Annotated[datetime | None, Field(exclude=True)] = None
    modified_by: Annotated[int | None, Field(exclude=True)] = None
