from __future__ import annotations

from datetime import datetime
from typing import Annotated, TYPE_CHECKING

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints

if TYPE_CHECKING:
    from .language_schema import LanguagePlainSchema


class TranslationStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    value: Constraints.String1000
    language_id: Constraints.PositiveInteger


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
