from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class LanguageStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    symbol: Constraints.Symbol
    description: Constraints.String1000Optional


class LanguagePlainSchema(BasePlainSchema):
    key: str
    symbol: str
    description: str | None
