from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class UnitStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    symbol: Constraints.Symbol
    description: Constraints.String1000Optional


class UnitPlainSchema(BasePlainSchema):
    key: str
    symbol: str
    description: str
