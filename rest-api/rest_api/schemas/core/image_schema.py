from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ImageStrictCreateSchema(BaseStrictSchema):
    is_primary: Constraints.BooleanFalse
    order: Constraints.PositiveInteger
    description: Constraints.StringOptional_1000
    content_type: Constraints.String_20
    data: Constraints.Bytes
    item_id: Constraints.PositiveInteger


class ImageStrictUpdateSchema(BaseStrictSchema):
    is_primary: Constraints.BooleanFalse
    order: Constraints.PositiveInteger


class ImageMultipartPayloadSchema(BaseStrictSchema):
    data: dict[str, str]
    files: dict[str, tuple[str, bytes, str]]


class ImageModelSchema(BaseStrictSchema):
    url: str
    is_primary: bool
    order: int
    description: str | None
    item_id: int


class ImagePlainSchema(BasePlainSchema):
    url: str
    is_primary: bool
    order: int
    description: str | None
