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


class OrderViewTargetItemSchema(BaseSchema):
    id: int
    item_id: int
    index: str
    name: str
    quantity: int
    purchase_price: float
    vat_rate: float


class OrderViewStatusHistorySchema(BaseSchema):
    status_id: int
    key: str
    created_at: datetime


class OrderViewResponseSchema(BaseSchema):
    order: OrderPlainSchema | None
    suppliers: list[OrderViewSupplierSchema]
    customers: list[OrderViewLookupSchema]
    currencies: list[OrderViewLookupSchema]
    delivery_methods: list[OrderViewLookupSchema]
    statuses: list[OrderViewLookupSchema]
    source_items: list[OrderViewSourceItemSchema]
    target_items: list[OrderViewTargetItemSchema]
    status_history: list[OrderViewStatusHistorySchema]
    categories: list[OrderViewLookupSchema] = Field(default_factory=list)
