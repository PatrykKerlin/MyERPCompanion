from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class CurrencyStrictSchema(BaseStrictSchema):
    code: Constraints.Symbol
    name: Constraints.String20
    sign: Constraints.Symbol


class CurrencyPlainSchema(BasePlainSchema):
    code: str
    name: str
    sign: str
