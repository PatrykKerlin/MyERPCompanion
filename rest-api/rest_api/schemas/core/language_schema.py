from typing import Annotated

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema


class LanguageStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=2, max_length=2)]


class LanguagePlainSchema(BasePlainSchema):
    key: str
