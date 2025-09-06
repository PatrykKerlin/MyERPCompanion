from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class ThemeStrictSchema(BaseStrictSchema):
    key: Constraints.Key


class ThemePlainSchema(BasePlainSchema):
    key: str
