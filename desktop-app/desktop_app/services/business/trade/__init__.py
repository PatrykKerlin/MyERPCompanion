from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    name_prefix="Currency",
    plain_schema_cls=CurrencyPlainSchema,
    strict_schema_cls=CurrencyStrictSchema,
)
CustomerService = ServiceFactory.create(
    name_prefix="Customer",
    plain_schema_cls=CustomerPlainSchema,
    strict_schema_cls=CustomerStrictSchema,
)
DiscountService = ServiceFactory.create(
    name_prefix="Discount",
    plain_schema_cls=DiscountPlainSchema,
    strict_schema_cls=DiscountStrictSchema,
)
SupplierService = ServiceFactory.create(
    name_prefix="Supplier",
    plain_schema_cls=SupplierPlainSchema,
    strict_schema_cls=SupplierStrictSchema,
)

__all__ = [
    "CurrencyService",
    "CustomerService",
    "DiscountService",
    "SupplierService",
]
