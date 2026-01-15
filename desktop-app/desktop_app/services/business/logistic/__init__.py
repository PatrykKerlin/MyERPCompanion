from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from schemas.business.logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
from utils.service_factory import ServiceFactory


AssocBinItemService = ServiceFactory.create(
    name_prefix="AssocBinItem",
    plain_schema_cls=AssocBinItemPlainSchema,
    strict_schema_cls=AssocBinItemStrictSchema,
)
BinService = ServiceFactory.create(
    name_prefix="Bin",
    plain_schema_cls=BinPlainSchema,
    strict_schema_cls=BinStrictSchema,
)
CarrierService = ServiceFactory.create(
    name_prefix="Carrier",
    plain_schema_cls=CarrierPlainSchema,
    strict_schema_cls=CarrierStrictSchema,
)
CategoryService = ServiceFactory.create(
    name_prefix="Category",
    plain_schema_cls=CategoryPlainSchema,
    strict_schema_cls=CategoryStrictSchema,
)
DeliveryMethodService = ServiceFactory.create(
    name_prefix="DeliveryMethod",
    plain_schema_cls=DeliveryMethodPlainSchema,
    strict_schema_cls=DeliveryMethodStrictSchema,
)
ItemService = ServiceFactory.create(
    name_prefix="ItemMethod",
    plain_schema_cls=ItemPlainSchema,
    strict_schema_cls=ItemStrictSchema,
)
UnitService = ServiceFactory.create(
    name_prefix="Unit",
    plain_schema_cls=UnitPlainSchema,
    strict_schema_cls=UnitStrictSchema,
)
WarehouseService = ServiceFactory.create(
    name_prefix="Warehouse",
    plain_schema_cls=WarehousePlainSchema,
    strict_schema_cls=WarehouseStrictSchema,
)


__all__ = [
    "AssocBinItemService",
    "BinService",
    "CarrierService",
    "CategoryService",
    "DeliveryMethodService",
    "ItemService",
    "UnitService",
    "WarehouseService",
]
