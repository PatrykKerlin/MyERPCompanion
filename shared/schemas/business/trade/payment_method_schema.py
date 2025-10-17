from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class PaymentMethodStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.String1000Optional
    provider: Constraints.String50
    api_url: Constraints.String1000
    surcharge_percent: Constraints.PercentFloat


class PaymentMethodPlainSchema(BasePlainSchema):
    name: str
    description: str | None
    provider: str
    api_url: str
    surcharge_percent: float
