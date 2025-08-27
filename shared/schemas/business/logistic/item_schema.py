from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import model_validator, field_validator

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers


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

    currency: int
    category: int
    unit: int
    supplier: int
    images: list[int]

    # bins: list[int]
    # discounts: list[int]
    # images: list[int]

    # @field_validator("bins", mode="before")
    # @classmethod
    # def _normalize_bins(cls, bins: Any) -> list[int]:
    #     return Normalizers.normalize_related_ids(bins)

    # @field_validator("discounts", mode="before")
    # @classmethod
    # def _normalize_discounts(cls, discounts: Any) -> list[int]:
    #     return Normalizers.normalize_related_ids(discounts)

    # @field_validator("images", mode="before")
    # @classmethod
    # def _normalize_images(cls, images: Any) -> list[int]:
    #     return Normalizers.normalize_related_ids(images)
