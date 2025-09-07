from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class ViewStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    in_menu: Constraints.BooleanTrue
    order: Constraints.PositiveInteger
    controllers: Constraints.String50List
    module_id: Constraints.PositiveInteger


class ViewPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    in_menu: bool
    order: int
    controllers: list[str]
    module_id: int
