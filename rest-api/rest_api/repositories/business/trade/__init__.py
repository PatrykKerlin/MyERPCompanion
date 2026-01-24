from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.currency import Currency
from models.business.trade.supplier import Supplier
from utils.repository_factory import RepositoryFactory
from repositories.business.trade.customer_repository import CustomerRepository
from repositories.business.trade.discount_repository import DiscountRepository
from repositories.business.trade.exchange_rate_repository import ExchangeRateRepository
from repositories.business.trade.order_repository import OrderRepository
from repositories.business.trade.status_repository import StatusRepository


AssocCategoryDiscountRepository = RepositoryFactory.create(AssocCategoryDiscount)
AssocCustomerDiscountRepository = RepositoryFactory.create(AssocCustomerDiscount)
AssocItemDiscountRepository = RepositoryFactory.create(AssocItemDiscount)
AssocOrderItemRepository = RepositoryFactory.create(AssocOrderItem)
AssocOrderStatusRepository = RepositoryFactory.create(AssocOrderStatus)
CurrencyRepository = RepositoryFactory.create(Currency)
SupplierRepository = RepositoryFactory.create(Supplier)


__all__ = [
    "AssocCategoryDiscountRepository",
    "AssocCustomerDiscountRepository",
    "AssocItemDiscountRepository",
    "AssocOrderItemRepository",
    "AssocOrderStatusRepository",
    "CurrencyRepository",
    "CustomerRepository",
    "DiscountRepository",
    "ExchangeRateRepository",
    "OrderRepository",
    "StatusRepository",
    "SupplierRepository",
]
