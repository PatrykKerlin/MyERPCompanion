from schemas.business.trade.assoc_category_discount_schema import (
    AssocCategoryDiscountPlainSchema,
    AssocCategoryDiscountStrictSchema,
)
from schemas.business.trade.assoc_customer_discount_schema import (
    AssocCustomerDiscountPlainSchema,
    AssocCustomerDiscountStrictSchema,
)
from schemas.business.trade.assoc_item_discount_schema import (
    AssocItemDiscountPlainSchema,
    AssocItemDiscountStrictSchema,
)
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.exchange_rate_schema import ExchangeRatePlainSchema, ExchangeRateStrictSchema
from schemas.business.trade.payment_method_schema import PaymentMethodPlainSchema, PaymentMethodStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from utils.service_factory import ServiceFactory


AssocCategoryDiscountService = ServiceFactory.create(
    name_prefix="AssocCategoryDiscount",
    plain_schema_cls=AssocCategoryDiscountPlainSchema,
    strict_schema_cls=AssocCategoryDiscountStrictSchema,
)
AssocCustomerDiscountService = ServiceFactory.create(
    name_prefix="AssocCustomerDiscount",
    plain_schema_cls=AssocCustomerDiscountPlainSchema,
    strict_schema_cls=AssocCustomerDiscountStrictSchema,
)
AssocItemDiscountService = ServiceFactory.create(
    name_prefix="AssocItemDiscount",
    plain_schema_cls=AssocItemDiscountPlainSchema,
    strict_schema_cls=AssocItemDiscountStrictSchema,
)
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
ExchangeRateService = ServiceFactory.create(
    name_prefix="ExchangeRate",
    plain_schema_cls=ExchangeRatePlainSchema,
    strict_schema_cls=ExchangeRateStrictSchema,
)
PaymentMethodService = ServiceFactory.create(
    name_prefix="PaymentMethod",
    plain_schema_cls=PaymentMethodPlainSchema,
    strict_schema_cls=PaymentMethodStrictSchema,
)
SupplierService = ServiceFactory.create(
    name_prefix="Supplier",
    plain_schema_cls=SupplierPlainSchema,
    strict_schema_cls=SupplierStrictSchema,
)


__all__ = [
    "AssocCategoryDiscountService",
    "AssocCustomerDiscountService",
    "AssocItemDiscountService",
    "CurrencyService",
    "CustomerService",
    "DiscountService",
    "ExchangeRateService",
    "PaymentMethodService",
    "SupplierService",
]
