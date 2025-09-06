from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class StatusStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    step_number: Constraints.PositiveInteger


class StatusPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    step_number: int
