from schemas.business.trade.assoc_order_item_schema import (
    AssocOrderItemPlainSchema,
    AssocOrderItemStrictSchema,
)
from schemas.business.trade.assoc_order_status_schema import (
    AssocOrderStatusPlainSchema,
    AssocOrderStatusStrictSchema,
)
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.status_schema import StatusPlainSchema, StatusStrictSchema
from services.business.trade.order_service import OrderService
from utils.service_factory import ServiceFactory

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
StatusService = ServiceFactory.create(
    name_prefix="Status",
    plain_schema_cls=StatusPlainSchema,
    strict_schema_cls=StatusStrictSchema,
)

__all__ = [
    "AssocOrderItemService",
    "AssocOrderStatusService",
    "CustomerService",
    "OrderService",
    "StatusService",
]
