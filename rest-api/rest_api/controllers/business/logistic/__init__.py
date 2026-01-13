from models.business.logistic.bin import Bin
from models.business.logistic.assoc_bin_item import AssocBinItem
from models.business.logistic.carrier import Carrier
from models.business.logistic.category import Category
from models.business.logistic.delivery_method import DeliveryMethod
from models.business.logistic.item import Item
from models.business.logistic.unit import Unit
from models.business.logistic.warehouse import Warehouse
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from services.business.logistic import (
    AssocBinItemService,
    BinService,
    CarrierService,
    CategoryService,
    ItemService,
    WarehouseService,
    UnitService,
    DeliveryMethodService,
)
from utils.controller_factory import ControllerFactory
from utils.enums import Action


AssocBinItemController = ControllerFactory.create(
    model_cls=AssocBinItem,
    service_cls=AssocBinItemService,
    input_schema_cls=AssocBinItemStrictSchema,
    output_schema_cls=AssocBinItemPlainSchema,
    include={
        Action.GET_BULK: True,
        Action.CREATE_BULK: True,
        Action.UPDATE_BULK: True,
        Action.DELETE_BULK: True,
    },
)
BinController = ControllerFactory.create(
    model_cls=Bin,
    service_cls=BinService,
    input_schema_cls=BinStrictSchema,
    output_schema_cls=BinPlainSchema,
)
CarrierController = ControllerFactory.create(
    model_cls=Carrier,
    service_cls=CarrierService,
    input_schema_cls=CarrierStrictSchema,
    output_schema_cls=CarrierPlainSchema,
)
CategoryController = ControllerFactory.create(
    model_cls=Category,
    service_cls=CategoryService,
    input_schema_cls=CategoryStrictSchema,
    output_schema_cls=CategoryPlainSchema,
)
DeliveryMethodController = ControllerFactory.create(
    model_cls=DeliveryMethod,
    service_cls=DeliveryMethodService,
    input_schema_cls=DeliveryMethodStrictSchema,
    output_schema_cls=DeliveryMethodPlainSchema,
)
ItemController = ControllerFactory.create(
    model_cls=Item,
    service_cls=ItemService,
    input_schema_cls=ItemStrictSchema,
    output_schema_cls=ItemPlainSchema,
    include={
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.GET_ONE: True,
        Action.CREATE: True,
        Action.UPDATE: True,
        Action.DELETE: True,
    },
)
UnitController = ControllerFactory.create(
    model_cls=Unit,
    service_cls=UnitService,
    input_schema_cls=UnitStrictSchema,
    output_schema_cls=UnitPlainSchema,
)
WarehouseController = ControllerFactory.create(
    model_cls=Warehouse,
    service_cls=WarehouseService,
    input_schema_cls=WarehouseStrictSchema,
    output_schema_cls=WarehousePlainSchema,
)


__all__ = [
    "BinController",
    "CarrierController",
    "CategoryController",
    "DeliveryMethodController",
    "ItemController",
    "UnitController",
    "WarehouseController",
]
