from models.business.trade.currency import Currency
from utils.repository_factory import RepositoryFactory

CurrencyRepository = RepositoryFactory.create(Currency)

__all__ = [
    "CurrencyRepository",
]
