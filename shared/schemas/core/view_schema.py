from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ViewStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    order: Constraints.PositiveInteger
    module_id: Constraints.PositiveInteger


class ViewPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int
    module_id: int
