from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class UnitStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    symbol: Constraints.Symbol
    description: Constraints.String1000Optional


class UnitPlainSchema(BasePlainSchema):
    key: str
    symbol: str
    description: str
