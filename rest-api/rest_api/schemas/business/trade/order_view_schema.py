from __future__ import annotations

from datetime import date, datetime

from pydantic import Field
from schemas.base.base_schema import BaseSchema
from schemas.business.trade.order_schema import OrderPlainSchema


class OrderViewImageSchema(BaseSchema):
    url: str | None = None
    is_primary: bool | None = None
    order: int | None = None
    description: str | None = None
    item_id: int | None = None


class OrderViewLookupSchema(BaseSchema):
    id: int
    label: str
    status_number: int | None = None


class OrderViewDiscountSchema(BaseSchema):
    id: int
    code: str
    percent: float | None = None
    min_value: float | None = None
    min_quantity: int | None = None
    currency_id: int | None = None


class OrderViewCustomerSchema(BaseSchema):
    id: int
    label: str
    discounts: list[OrderViewDiscountSchema]


class OrderViewCategorySchema(BaseSchema):
    id: int
    label: str
    discounts: list[OrderViewDiscountSchema]


class OrderViewSupplierSchema(BaseSchema):
    id: int
    label: str
    currency_id: int


class OrderViewSourceItemSchema(BaseSchema):
    id: int
    index: str
    name: str
    ean: str
    description: str | None = None
    purchase_price: float
    vat_rate: float
    is_fragile: bool | None = None
    category_id: int | None = None
    category_name: str | None = None
    width: float
    height: float
    length: float
    weight: float
    expiration_date: date | None = None
    stock_quantity: int = 0
    reserved_quantity: int = 0
    outbound_quantity: int = 0
    moq: int = 1
    is_package: bool = False
    supplier_currency_id: int | None = None
    discounts: list[OrderViewDiscountSchema]
    images: list[OrderViewImageSchema] = Field(default_factory=list)


class OrderViewTargetItemSchema(BaseSchema):
    id: int
    item_id: int
    index: str
    name: str
    quantity: int
    purchase_price: float
    vat_rate: float
    width: float
    height: float
    length: float
    weight: float
    category_id: int | None = None
    supplier_currency_id: int | None = None
    bin_id: int | None = None
    category_discount_id: int | None = None
    customer_discount_id: int | None = None
    item_discount_id: int | None = None


class OrderViewStatusHistorySchema(BaseSchema):
    status_id: int
    key: str
    created_at: datetime


class OrderViewDeliveryMethodSchema(BaseSchema):
    id: int
    label: str
    price_per_unit: float
    max_width: float
    max_height: float
    max_length: float
    max_weight: float
    carrier_currency_id: int | None = None


class OrderViewExchangeRateSchema(BaseSchema):
    rate: float | None = None
    base_currency_id: int
    quote_currency_id: int


class OrderViewResponseSchema(BaseSchema):
    order: OrderPlainSchema | None = None
    suppliers: list[OrderViewSupplierSchema]
    customers: list[OrderViewCustomerSchema]
    currencies: list[OrderViewLookupSchema]
    delivery_methods: list[OrderViewDeliveryMethodSchema]
    statuses: list[OrderViewLookupSchema]
    source_items: list[OrderViewSourceItemSchema]
    target_items: list[OrderViewTargetItemSchema]
    status_history: list[OrderViewStatusHistorySchema]
    categories: list[OrderViewCategorySchema] = Field(default_factory=list)
    exchange_rates: list[OrderViewExchangeRateSchema] | None = None
