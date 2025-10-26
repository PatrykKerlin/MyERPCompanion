from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from schemas.business.logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
from utils.service_factory import ServiceFactory

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
DeliveryMethodService = ServiceFactory.create(
    name_prefix="DeliveryMethod",
    plain_schema_cls=DeliveryMethodPlainSchema,
    strict_schema_cls=DeliveryMethodStrictSchema,
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
    "BinService",
    "CarrierService",
    "DeliveryMethodService",
    "UnitService",
    "WarehouseService",
]
