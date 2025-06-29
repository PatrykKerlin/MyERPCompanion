from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema, BasePlainSchema


class LanguageStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=2, max_length=2)]


class LanguagePlainSchema(BasePlainSchema):
    key: str
