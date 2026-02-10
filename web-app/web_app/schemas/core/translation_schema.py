from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class TranslationStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    value: Constraints.String_1000
    language_id: Constraints.PositiveInteger


class TranslationPlainSchema(BasePlainSchema):
    key: str
    value: str
    language_id: int
