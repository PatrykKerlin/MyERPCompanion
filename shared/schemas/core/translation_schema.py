from datetime import datetime
from typing import Annotated

from pydantic import Field

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class TranslationStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    value: Constraints.String_1000
    language_id: Constraints.PositiveInteger


class TranslationPlainSchema(BasePlainSchema):
    key: str
    value: str
    language_id: int


class TranslationByLanguagePlainSchema(BasePlainSchema):
    key: str
    value: str
    is_active: Annotated[bool, Field(exclude=True)]
    created_at: Annotated[datetime, Field(exclude=True)]
    created_by: Annotated[int, Field(exclude=True)]
    modified_at: Annotated[datetime | None, Field(exclude=True)] = None
    modified_by: Annotated[int | None, Field(exclude=True)] = None
