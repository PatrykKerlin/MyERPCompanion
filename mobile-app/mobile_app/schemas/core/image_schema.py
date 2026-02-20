from schemas.base.base_schema import BasePlainSchema


class ImagePlainSchema(BasePlainSchema):
    url: str
    is_primary: bool
    order: int
    description: str | None
