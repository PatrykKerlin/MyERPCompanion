from models.business.logistic.bin import Bin
from models.business.logistic.warehouse import Warehouse
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from services.business.logistic import BinService, WarehouseService
from utils.controller_factory import ControllerFactory

BinController = ControllerFactory.create(
    model_cls=Bin,
    service_cls=BinService,
    input_schema_cls=BinStrictSchema,
    output_schema_cls=BinPlainSchema,
)
WarehouseController = ControllerFactory.create(
    model_cls=Warehouse,
    service_cls=WarehouseService,
    input_schema_cls=WarehouseStrictSchema,
    output_schema_cls=WarehousePlainSchema,
)

__all__ = [
    "BinController",
    "WarehouseController",
]
