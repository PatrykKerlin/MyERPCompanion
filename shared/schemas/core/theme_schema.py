from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ThemeStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    value: Constraints.String20


class ThemePlainSchema(BasePlainSchema):
    key: str
    value: str
