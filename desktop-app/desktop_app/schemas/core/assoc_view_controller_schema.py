from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocViewControllerStrictSchema(BaseStrictSchema):
    view_id: Constraints.PositiveInteger
    controller_id: Constraints.PositiveInteger


class AssocViewControllerPlainSchema(BasePlainSchema):
    view_id: int
    controller_id: int
