from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class UnitStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    symbol: Constraints.Symbol
    description: Constraints.String1000Optional


class UnitPlainSchema(BasePlainSchema):
    name: str
    symbol: str
    description: str
