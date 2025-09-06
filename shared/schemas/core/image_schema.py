from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class ImageStrictSchema(BaseStrictSchema):
    url: Constraints.String1000
    is_primary: Constraints.BooleanFalse
    order: Constraints.PositiveInteger
    description: Constraints.String1000Optional


class ImagePlainSchema(BasePlainSchema):
    url: str
    is_primary: bool
    order: int
    description: str | None
