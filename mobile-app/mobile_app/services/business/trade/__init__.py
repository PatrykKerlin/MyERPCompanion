from schemas.business.trade.assoc_item_discount_schema import (
    AssocItemDiscountPlainSchema,
    AssocItemDiscountStrictSchema,
)
from schemas.business.trade.assoc_order_item_schema import (
    AssocOrderItemPlainSchema,
    AssocOrderItemStrictSchema,
)
from schemas.business.trade.assoc_order_status_schema import (
    AssocOrderStatusPlainSchema,
    AssocOrderStatusStrictSchema,
)
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.status_schema import StatusPlainSchema, StatusStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from services.business.trade.order_service import OrderService
from utils.service_factory import ServiceFactory

AssocItemDiscountService = ServiceFactory.create(
    name_prefix="AssocItemDiscount",
    plain_schema_cls=AssocItemDiscountPlainSchema,
    strict_schema_cls=AssocItemDiscountStrictSchema,
)
AssocOrderItemService = ServiceFactory.create(
    name_prefix="AssocOrderItem",
    plain_schema_cls=AssocOrderItemPlainSchema,
    strict_schema_cls=AssocOrderItemStrictSchema,
)
AssocOrderStatusService = ServiceFactory.create(
    name_prefix="AssocOrderStatus",
    plain_schema_cls=AssocOrderStatusPlainSchema,
    strict_schema_cls=AssocOrderStatusStrictSchema,
)
CustomerService = ServiceFactory.create(
    name_prefix="Customer",
    plain_schema_cls=CustomerPlainSchema,
    strict_schema_cls=CustomerStrictSchema,
)
DiscountService = ServiceFactory.create(
    name_prefix="Discount",
    plain_schema_cls=DiscountPlainSchema,
    strict_schema_cls=DiscountStrictSchema,
)
StatusService = ServiceFactory.create(
    name_prefix="Status",
    plain_schema_cls=StatusPlainSchema,
    strict_schema_cls=StatusStrictSchema,
)
SupplierService = ServiceFactory.create(
    name_prefix="Supplier",
    plain_schema_cls=SupplierPlainSchema,
    strict_schema_cls=SupplierStrictSchema,
)

__all__ = [
    "AssocItemDiscountService",
    "AssocOrderItemService",
    "AssocOrderStatusService",
    "CustomerService",
    "DiscountService",
    "OrderService",
    "StatusService",
    "SupplierService",
]
