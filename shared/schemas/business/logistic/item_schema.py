from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import Field, field_validator, model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.image_schema import ImagePlainSchema
from schemas.validation.constraints import Constraints
from schemas.validation.normalizers import Normalizers


class ItemStrictSchema(BaseStrictSchema):
    index: Constraints.String_10
    name: Constraints.Name
    ean: Constraints.Ean
    description: Constraints.StringOptional_1000

    purchase_price: Constraints.PositiveNumeric_10_2
    vat_rate: Constraints.PercentFloat
    margin: Constraints.PositiveNumeric_6_3

    is_available: Constraints.BooleanTrue
    is_fragile: Constraints.BooleanFalse
    is_package: Constraints.BooleanFalse
    is_returnable: Constraints.BooleanFalse

    width: Constraints.PositiveNumeric_6_3
    height: Constraints.PositiveNumeric_6_3
    length: Constraints.PositiveNumeric_6_3
    weight: Constraints.PositiveNumeric_6_3
    expiration_date: date | None

    stock_quantity: Constraints.Quantity
    min_stock_level: Constraints.Quantity
    max_stock_level: Constraints.PositiveIntegerOptional
    moq: Constraints.PositiveInteger

    currency_id: Constraints.PositiveInteger
    category_id: Constraints.PositiveInteger
    unit_id: Constraints.PositiveInteger
    supplier_id: Constraints.PositiveInteger

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
    ean: str
    description: str

    purchase_price: float
    vat_rate: float
    margin: float

    is_available: bool
    is_fragile: bool
    is_package: bool
    is_returnable: bool

    width: float
    height: float
    length: float
    weight: float
    expiration_date: date | None

    stock_quantity: int
    min_stock_level: int
    max_stock_level: int | None
    moq: int

    currency_id: int
    category_id: int
    unit_id: int
    supplier_id: int

    images: list[ImagePlainSchema]

    bin_ids: list[int] = Field(alias="bins")
    discount_ids: list[int] = Field(alias="discounts")

    @field_validator("bin_ids", mode="before")
    @classmethod
    def _normalize_bins(cls, values: list[Any]) -> list[int]:
        return Normalizers.normalize_related_ids(values)

    @field_validator("discount_ids", mode="before")
    @classmethod
    def _normalize_discounts(cls, values: list[Any]) -> list[int]:
        return Normalizers.normalize_related_ids(values)
