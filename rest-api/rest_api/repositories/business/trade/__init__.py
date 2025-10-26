from models.business.trade.currency import Currency
from models.business.trade.supplier import Supplier
from utils.repository_factory import RepositoryFactory

CurrencyRepository = RepositoryFactory.create(Currency)
SupplierRepository = RepositoryFactory.create(Supplier)

__all__ = [
    "CurrencyRepository",
    "SupplierRepository",
]
