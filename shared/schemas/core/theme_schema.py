from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class ThemeStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    value: Constraints.String20


class ThemePlainSchema(BasePlainSchema):
    key: str
    value: str
