from models.business.logistic.bin import Bin
from models.business.logistic.warehouse import Warehouse
from repositories.business.logistic import BinRepository, WarehouseRepository
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from utils.service_factory import ServiceFactory

BinService = ServiceFactory.create(
    model_cls=Bin,
    repository_cls=BinRepository,
    input_schema_cls=BinStrictSchema,
    output_schema_cls=BinPlainSchema,
)
WarehouseService = ServiceFactory.create(
    model_cls=Warehouse,
    repository_cls=WarehouseRepository,
    input_schema_cls=WarehouseStrictSchema,
    output_schema_cls=WarehousePlainSchema,
)

__all__ = [
    "BinService",
    "WarehouseService",
]
