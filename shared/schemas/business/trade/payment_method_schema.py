from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class PaymentMethodStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional

    provider: Constraints.String50
    api_url: Constraints.String1000
    surcharge_percent: Constraints.PercentFloat


class PaymentMethodPlainSchema(BasePlainSchema):
    key: str
    description: str | None

    provider: str
    api_url: str
    surcharge_percent: float
