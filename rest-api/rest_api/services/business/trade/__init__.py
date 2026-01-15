from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from models.business.trade.discount import Discount
from models.business.trade.supplier import Supplier
from repositories.business.trade import CurrencyRepository, SupplierRepository
from repositories.business.trade.customer_repository import CustomerRepository
from repositories.business.trade.discount_repository import DiscountRepository
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    model_cls=Currency,
    repository_cls=CurrencyRepository,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)
CustomerService = ServiceFactory.create(
    model_cls=Customer,
    repository_cls=CustomerRepository,
    input_schema_cls=CustomerStrictSchema,
    output_schema_cls=CustomerPlainSchema,
)
DiscountService = ServiceFactory.create(
    model_cls=Discount,
    repository_cls=DiscountRepository,
    input_schema_cls=DiscountStrictSchema,
    output_schema_cls=DiscountPlainSchema,
)
SupplierService = ServiceFactory.create(
    model_cls=Supplier,
    repository_cls=SupplierRepository,
    input_schema_cls=SupplierStrictSchema,
    output_schema_cls=SupplierPlainSchema,
)


__all__ = [
    "CurrencyService",
    "CustomerService",
    "DiscountService",
    "SupplierService",
]
