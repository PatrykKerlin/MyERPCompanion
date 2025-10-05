from typing import TYPE_CHECKING

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints

if TYPE_CHECKING:
    from ..trade.discount_schema import DiscountPlainSchema


class CategoryStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.String1000Optional


class CategoryPlainSchema(BasePlainSchema):
    name: str
    description: str | None
    discounts: list[DiscountPlainSchema]
