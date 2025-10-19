from repositories.business.logistic.bin_repository import BinRepository
from models.business.logistic.warehouse import Warehouse
from utils.repository_factory import RepositoryFactory

WarehouseRepository = RepositoryFactory.create(Warehouse)

__all__ = [
    "BinRepository",
    "WarehouseRepository",
]
