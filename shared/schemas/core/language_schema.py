from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class LanguageStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    symbol: Constraints.Symbol
    description: Constraints.StringOptional_1000


class LanguagePlainSchema(BasePlainSchema):
    key: str
    symbol: str
    description: str | None
