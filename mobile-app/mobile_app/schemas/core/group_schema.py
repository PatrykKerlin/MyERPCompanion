from schemas.base.base_schema import BasePlainSchema


class GroupPlainSchema(BasePlainSchema):
    key: str
    description: str | None
