from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class CategoryStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional


class CategoryPlainSchema(BasePlainSchema):
    key: str
    description: str | None
