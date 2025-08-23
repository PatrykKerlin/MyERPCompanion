from __future__ import annotations

from datetime import date
from typing import Annotated, TYPE_CHECKING

from pydantic import Field, model_validator

from schemas.base import BaseStrictSchema, BasePlainSchema

if TYPE_CHECKING:
    from .currency_schema import CurrencyPlainSchema
    from .category_schema import CategoryPlainSchema
    from .unit_schema import UnitPlainSchema
    from .supplier_schema import SupplierPlainSchema


class ItemStrictSchema(BaseStrictSchema):
    index: Annotated[str, Field(min_length=10, max_length=10)]
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(min_length=1, max_length=255)]

    ean: Annotated[str, Field(pattern=r"^\d{13}$")]
    sku: Annotated[str, Field(min_length=1, max_length=25)]

    purchase_price: Annotated[float, Field(gt=0)]
    vat_rate: Annotated[float | None, Field(ge=0, le=1)]
    margin: Annotated[float, Field(ge=0, le=100)]

    is_available: Annotated[bool, Field(default=True)]
    is_fragile: Annotated[bool, Field(default=False)]
    is_package: Annotated[bool, Field(default=False)]
    is_returnable: Annotated[bool, Field(default=False)]

    expiration_date: date | None

    width: Annotated[float, Field(gt=0)]
    height: Annotated[float, Field(gt=0)]
    length: Annotated[float, Field(gt=0)]
    weight: Annotated[float, Field(gt=0)]

    stock_quantity: Annotated[int, Field(gt=0)]
    min_stock_level: Annotated[int, Field(ge=1)]
    max_stock_level: Annotated[int | None, Field(ge=1)]
    moq: Annotated[int, Field(ge=1)]

    currency_id: Annotated[int, Field(ge=1)]
    category_id: Annotated[int, Field(ge=1)]
    unit_id: Annotated[int, Field(ge=1)]
    supplier_id: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def _validate_business_rules(self) -> ItemStrictSchema:
        today = date.today()

        if self.expiration_date is not None and self.expiration_date < today:
            raise ValueError("expiration_date must be today or later")

        if self.max_stock_level is not None and self.max_stock_level < self.min_stock_level:
            raise ValueError("max_stock_level cannot be lower than min_stock_level")

        if self.max_stock_level is not None and self.stock_quantity > self.max_stock_level:
            raise ValueError("stock_quantity cannot exceed max_stock_level")

        if self.stock_quantity < self.moq:
            raise ValueError("stock_quantity cannot be lower than moq")

        return self


class ItemPlainSchema(BasePlainSchema):
    index: str
    name: str
    description: str

    ean: str
    sku: str

    purchase_price: float
    vat_rate: float | None
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

    currency: CurrencyPlainSchema
    category: CategoryPlainSchema
    unit: UnitPlainSchema
    supplier: SupplierPlainSchema

    bins: list[int] = Field(default_factory=list)
    discounts: list[int] = Field(default_factory=list)
    orders: list[int] = Field(default_factory=list)
