from models.business.logistic.category import Category
from models.business.logistic.delivery_method import DeliveryMethod
from models.business.logistic.unit import Unit
from models.business.logistic.warehouse import Warehouse
from repositories.business.logistic.bin_repository import BinRepository
from repositories.business.logistic.carrier_repository import CarrierRepository
from repositories.business.logistic.item_repository import ItemRepository
from utils.repository_factory import RepositoryFactory


CategoryRepository = RepositoryFactory.create(Category)
DeliveryMethodRepository = RepositoryFactory.create(DeliveryMethod)
UnitRepository = RepositoryFactory.create(Unit)
WarehouseRepository = RepositoryFactory.create(Warehouse)


__all__ = [
    "BinRepository",
    "CarrierRepository",
    "CategoryRepository",
    "DeliveryMethodRepository",
    "ItemRepository",
    "UnitRepository",
    "WarehouseRepository",
]
