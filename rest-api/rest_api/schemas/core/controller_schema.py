from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ControllerStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    table: Constraints.StringOptional_50
    description: Constraints.StringOptional_1000


class ControllerPlainSchema(BasePlainSchema):
    name: str
    table: str | None
    description: str | None
