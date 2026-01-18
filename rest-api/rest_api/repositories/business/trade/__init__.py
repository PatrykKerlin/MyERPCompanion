from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.currency import Currency
from models.business.trade.payment_method import PaymentMethod
from models.business.trade.supplier import Supplier
from utils.repository_factory import RepositoryFactory

AssocCategoryDiscountRepository = RepositoryFactory.create(AssocCategoryDiscount)
AssocCustomerDiscountRepository = RepositoryFactory.create(AssocCustomerDiscount)
AssocItemDiscountRepository = RepositoryFactory.create(AssocItemDiscount)
AssocOrderItemRepository = RepositoryFactory.create(AssocOrderItem)
AssocOrderStatusRepository = RepositoryFactory.create(AssocOrderStatus)
CurrencyRepository = RepositoryFactory.create(Currency)
PaymentMethodRepository = RepositoryFactory.create(PaymentMethod)
SupplierRepository = RepositoryFactory.create(Supplier)


__all__ = [
    "AssocCategoryDiscountRepository",
    "AssocCustomerDiscountRepository",
    "AssocItemDiscountRepository",
    "AssocOrderItemRepository",
    "AssocOrderStatusRepository",
    "CurrencyRepository",
    "PaymentMethodRepository",
    "SupplierRepository",
]
