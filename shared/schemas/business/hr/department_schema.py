from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class DepartmentStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional


class DepartmentPlainSchema(BasePlainSchema):
    key: str
    description: str | None
