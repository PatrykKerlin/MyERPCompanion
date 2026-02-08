from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from utils.service_factory import ServiceFactory


ItemService = ServiceFactory.create(
    name_prefix="Item",
    plain_schema_cls=ItemPlainSchema,
    strict_schema_cls=ItemStrictSchema,
)

__all__ = [
    "ItemService",
]
