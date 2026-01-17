from models.business.trade.currency import Currency
from models.business.trade.payment_method import PaymentMethod
from models.business.trade.supplier import Supplier
from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from utils.repository_factory import RepositoryFactory


AssocCategoryDiscountRepository = RepositoryFactory.create(AssocCategoryDiscount)
AssocCustomerDiscountRepository = RepositoryFactory.create(AssocCustomerDiscount)
AssocItemDiscountRepository = RepositoryFactory.create(AssocItemDiscount)
CurrencyRepository = RepositoryFactory.create(Currency)
PaymentMethodRepository = RepositoryFactory.create(PaymentMethod)
SupplierRepository = RepositoryFactory.create(Supplier)


__all__ = [
    "AssocCategoryDiscountRepository",
    "AssocCustomerDiscountRepository",
    "AssocItemDiscountRepository",
    "CurrencyRepository",
    "PaymentMethodRepository",
    "SupplierRepository",
]
