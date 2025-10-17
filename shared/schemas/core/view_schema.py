from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ViewStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    order: Constraints.PositiveInteger
    controllers: Constraints.String50List
    module_id: Constraints.PositiveInteger


class ViewPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int
    controllers: list[str]
    module_id: int
