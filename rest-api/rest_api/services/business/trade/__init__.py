from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from models.business.trade.discount import Discount
from models.business.trade.exchange_rate import ExchangeRate
from models.business.trade.status import Status
from models.business.trade.supplier import Supplier
from repositories.business.trade import (
    AssocCategoryDiscountRepository,
    AssocCustomerDiscountRepository,
    AssocItemDiscountRepository,
    AssocOrderItemRepository,
    AssocOrderStatusRepository,
    CurrencyRepository,
    SupplierRepository,
)
from repositories.business.trade.customer_repository import CustomerRepository
from repositories.business.trade.discount_repository import DiscountRepository
from repositories.business.trade.exchange_rate_repository import ExchangeRateRepository
from repositories.business.trade.status_repository import StatusRepository
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
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.exchange_rate_schema import ExchangeRatePlainSchema, ExchangeRateStrictSchema
from schemas.business.trade.status_schema import StatusPlainSchema, StatusStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from services.business.trade.invoice_service import InvoiceService
from utils.service_factory import ServiceFactory

AssocCategoryDiscountService = ServiceFactory.create(
    model_cls=AssocCategoryDiscount,
    repository_cls=AssocCategoryDiscountRepository,
    input_schema_cls=AssocCategoryDiscountStrictSchema,
    output_schema_cls=AssocCategoryDiscountPlainSchema,
)
AssocCustomerDiscountService = ServiceFactory.create(
    model_cls=AssocCustomerDiscount,
    repository_cls=AssocCustomerDiscountRepository,
    input_schema_cls=AssocCustomerDiscountStrictSchema,
    output_schema_cls=AssocCustomerDiscountPlainSchema,
)
AssocItemDiscountService = ServiceFactory.create(
    model_cls=AssocItemDiscount,
    repository_cls=AssocItemDiscountRepository,
    input_schema_cls=AssocItemDiscountStrictSchema,
    output_schema_cls=AssocItemDiscountPlainSchema,
)
AssocOrderItemService = ServiceFactory.create(
    model_cls=AssocOrderItem,
    repository_cls=AssocOrderItemRepository,
    input_schema_cls=AssocOrderItemStrictSchema,
    output_schema_cls=AssocOrderItemPlainSchema,
)
AssocOrderStatusService = ServiceFactory.create(
    model_cls=AssocOrderStatus,
    repository_cls=AssocOrderStatusRepository,
    input_schema_cls=AssocOrderStatusStrictSchema,
    output_schema_cls=AssocOrderStatusPlainSchema,
)
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
ExchangeRateService = ServiceFactory.create(
    model_cls=ExchangeRate,
    repository_cls=ExchangeRateRepository,
    input_schema_cls=ExchangeRateStrictSchema,
    output_schema_cls=ExchangeRatePlainSchema,
)
StatusService = ServiceFactory.create(
    model_cls=Status,
    repository_cls=StatusRepository,
    input_schema_cls=StatusStrictSchema,
    output_schema_cls=StatusPlainSchema,
)
SupplierService = ServiceFactory.create(
    model_cls=Supplier,
    repository_cls=SupplierRepository,
    input_schema_cls=SupplierStrictSchema,
    output_schema_cls=SupplierPlainSchema,
)


__all__ = [
    "AssocCategoryDiscountService",
    "AssocCustomerDiscountService",
    "AssocItemDiscountService",
    "AssocOrderItemService",
    "AssocOrderStatusService",
    "CurrencyService",
    "CustomerService",
    "DiscountService",
    "ExchangeRateService",
    "InvoiceService",
    "StatusService",
    "SupplierService",
]
