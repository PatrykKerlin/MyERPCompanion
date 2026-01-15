from models.business.logistic.assoc_bin_item import AssocBinItem
from models.business.logistic.bin import Bin
from models.business.logistic.carrier import Carrier
from models.business.logistic.category import Category
from models.business.logistic.delivery_method import DeliveryMethod
from models.business.logistic.item import Item
from models.business.logistic.unit import Unit
from models.business.logistic.warehouse import Warehouse
from repositories.business.logistic import (
    AssocBinItemRepository,
    BinRepository,
    CarrierRepository,
    CategoryRepository,
    DeliveryMethodRepository,
    UnitRepository,
    WarehouseRepository,
)
from repositories.business.logistic.item_repository import ItemRepository
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from utils.service_factory import ServiceFactory

AssocBinItemService = ServiceFactory.create(
    model_cls=AssocBinItem,
    repository_cls=AssocBinItemRepository,
    input_schema_cls=AssocBinItemStrictSchema,
    output_schema_cls=AssocBinItemPlainSchema,
)
BinService = ServiceFactory.create(
    model_cls=Bin,
    repository_cls=BinRepository,
    input_schema_cls=BinStrictSchema,
    output_schema_cls=BinPlainSchema,
)
CarrierService = ServiceFactory.create(
    model_cls=Carrier,
    repository_cls=CarrierRepository,
    input_schema_cls=CarrierStrictSchema,
    output_schema_cls=CarrierPlainSchema,
)
CategoryService = ServiceFactory.create(
    model_cls=Category,
    repository_cls=CategoryRepository,
    input_schema_cls=CategoryStrictSchema,
    output_schema_cls=CategoryPlainSchema,
)
DeliveryMethodService = ServiceFactory.create(
    model_cls=DeliveryMethod,
    repository_cls=DeliveryMethodRepository,
    input_schema_cls=DeliveryMethodStrictSchema,
    output_schema_cls=DeliveryMethodPlainSchema,
)
ItemService = ServiceFactory.create(
    model_cls=Item,
    repository_cls=ItemRepository,
    input_schema_cls=ItemStrictSchema,
    output_schema_cls=ItemPlainSchema,
)
UnitService = ServiceFactory.create(
    model_cls=Unit,
    repository_cls=UnitRepository,
    input_schema_cls=UnitStrictSchema,
    output_schema_cls=UnitPlainSchema,
)
WarehouseService = ServiceFactory.create(
    model_cls=Warehouse,
    repository_cls=WarehouseRepository,
    input_schema_cls=WarehouseStrictSchema,
    output_schema_cls=WarehousePlainSchema,
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
