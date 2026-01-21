from __future__ import annotations

from datetime import datetime

from pydantic import Field

from schemas.base.base_schema import BaseSchema
from schemas.business.trade.order_schema import OrderPlainSchema


class OrderViewLookupSchema(BaseSchema):
    id: int
    label: str
    status_number: int | None = None


class OrderViewSupplierSchema(BaseSchema):
    id: int
    label: str
    currency_id: int


class OrderViewSourceItemSchema(BaseSchema):
    id: int
    index: str
    name: str
    ean: str
    purchase_price: float
    vat_rate: float
    category_id: int | None = None
    width: float
    height: float
    length: float
    weight: float
    stock_quantity: int = 0
    reserved_quantity: int = 0
    moq: int = 1
    is_package: bool = False
    supplier_currency_id: int | None = None


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
    order: OrderPlainSchema | None
    suppliers: list[OrderViewSupplierSchema]
    customers: list[OrderViewLookupSchema]
    currencies: list[OrderViewLookupSchema]
    delivery_methods: list[OrderViewDeliveryMethodSchema]
    statuses: list[OrderViewLookupSchema]
    source_items: list[OrderViewSourceItemSchema]
    target_items: list[OrderViewTargetItemSchema]
    status_history: list[OrderViewStatusHistorySchema]
    categories: list[OrderViewLookupSchema] = Field(default_factory=list)
    exchange_rates: list[OrderViewExchangeRateSchema] | None = None
