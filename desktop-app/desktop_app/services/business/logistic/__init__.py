from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
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
WarehouseService = ServiceFactory.create(
    name_prefix="Warehouse",
    plain_schema_cls=WarehousePlainSchema,
    strict_schema_cls=WarehouseStrictSchema,
)


__all__ = [
    "BinService",
    "CarrierService",
    "WarehouseService",
]
