from __future__ import annotations

from datetime import date
from typing import Any, TYPE_CHECKING

from pydantic import model_validator

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers

if TYPE_CHECKING:
    from ...core.image_schema import ImagePlainSchema
    from ..trade.discount_schema import DiscountPlainSchema


class ItemStrictSchema(BaseStrictSchema):
    index: Constraints.String10
    name: Constraints.String100
    description: Constraints.String1000Optional

    ean: Constraints.Ean

    purchase_price: Constraints.PositiveNumeric102
    vat_rate: Constraints.PercentFloat
    margin: Constraints.PositiveNumeric63

    is_available: Constraints.BooleanTrue
    is_fragile: Constraints.BooleanFalse
    is_package: Constraints.BooleanFalse
    is_returnable: Constraints.BooleanFalse

    expiration_date: date | None

    width: Constraints.PositiveNumeric63
    height: Constraints.PositiveNumeric63
    length: Constraints.PositiveNumeric63
    weight: Constraints.PositiveNumeric63

    stock_quantity: Constraints.Quantity
    min_stock_level: Constraints.Quantity
    max_stock_level: Constraints.PositiveIntegerOptional
    moq: Constraints.PositiveInteger

    currency_id: Constraints.PositiveInteger
    category_id: Constraints.PositiveInteger
    unit_id: Constraints.PositiveInteger
    supplier_id: Constraints.PositiveInteger

    images: Constraints.PositiveIntegerListOptional

    @model_validator(mode="after")
    def _validate_data(self) -> ItemStrictSchema:
        today = date.today()

        if self.expiration_date is not None and self.expiration_date < today:
            raise ValueError("expiration_date must be today or later")

        if self.max_stock_level is not None and self.stock_quantity > self.max_stock_level:
            raise ValueError("stock_quantity cannot exceed max_stock_level")

        return self


class ItemPlainSchema(BasePlainSchema):
    index: str
    name: str
    description: str

    ean: str

    purchase_price: float
    vat_rate: float
    margin: float

    is_available: bool
    is_fragile: bool
    is_package: bool
    is_returnable: bool

    expiration_date: date | None

    width: float
    height: float
    length: float
    weight: float

    stock_quantity: int
    min_stock_level: int
    max_stock_level: int | None
    moq: int

    currency_id: int
    category_id: int
    unit_id: int
    supplier_id: int

    discounts: list[DiscountPlainSchema]
    images: list[ImagePlainSchema]

    bin_ids: list[int]

    @model_validator(mode="before")
    @classmethod
    def _extract_bin_ids(cls, data: Any) -> Any:
        if isinstance(data, dict) and "bins" in data and "bin_ids" not in data:
            data["bin_ids"] = Normalizers.normalize_related_ids(data["bins"])
        return data
