from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class ThemeStrictSchema(BaseStrictSchema):
    key: Constraints.Key


class ThemePlainSchema(BasePlainSchema):
    key: str
