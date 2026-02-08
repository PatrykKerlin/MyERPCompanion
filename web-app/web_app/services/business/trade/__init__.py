from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from services.business.trade.order_view_service import OrderViewService
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
OrderService = ServiceFactory.create(
    name_prefix="Order",
    plain_schema_cls=OrderPlainSchema,
    strict_schema_cls=OrderStrictSchema,
)

__all__ = [
    "AssocOrderItemService",
    "AssocOrderStatusService",
    "OrderService",
    "OrderViewService",
]
