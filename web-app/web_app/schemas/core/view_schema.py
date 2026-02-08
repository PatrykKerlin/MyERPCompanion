from schemas.base.base_schema import BasePlainSchema


class ViewPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int
    module_id: int

    controller_ids: list[int]
