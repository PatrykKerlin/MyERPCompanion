from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class CurrencyStrictSchema(BaseStrictSchema):
    code: Constraints.Symbol
    name: Constraints.Name
    sign: Constraints.Symbol


class CurrencyPlainSchema(BasePlainSchema):
    code: str
    name: str
    sign: str
