from .hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from .hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from .hr.position_schema import PositionPlainSchema, PositionStrictSchema

# from .logistic.assoc_schema import AssocBinItemStrictSchema
# from .logistic.bin_schema import BinStrictSchema, BinPlainSchema
# from .logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
# from .logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
# from .logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
# from .logistic.item_schema import ItemPlainSchema, ItemStrictSchema
# from .logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
# from .logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
# from .trade.assoc_schema import (
#     AssocCategoryDiscountStrictSchema,
#     AssocCustomerDiscountStrictSchema,
#     AssocItemDiscountStrictSchema,
#     AssocOrderItemStrictSchema,
#     AssocOrderStatusStrictSchema,
# )
from .trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema

# from .trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
# from .trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
# from .trade.exchange_rate_schema import ExchangeRatePlainSchema, ExchangeRateStrictSchema
# from .trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
# from .trade.order_schema import OrderPlainSchema, OrderStrictSchema
# from .trade.payment_method_schema import PaymentMethodPlainSchema, PaymentMethodStrictSchema
# from .trade.status_schema import StatusPlainSchema, StatusStrictSchema
# from .trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema

__all__ = [
    "DepartmentPlainSchema",
    "DepartmentStrictSchema",
    "EmployeePlainSchema",
    "EmployeeStrictSchema",
    "PositionPlainSchema",
    "PositionStrictSchema",
    # "AssocBinItemStrictSchema",
    # "BinPlainSchema",
    # "BinStrictSchema",
    # "CarrierPlainSchema",
    # "CarrierStrictSchema",
    # "CategoryPlainSchema",
    # "CategoryStrictSchema",
    # "DeliveryMethodPlainSchema",
    # "DeliveryMethodStrictSchema",
    # "ItemPlainSchema",
    # "ItemStrictSchema",
    # "UnitPlainSchema",
    # "UnitStrictSchema",
    # "WarehousePlainSchema",
    # "WarehouseStrictSchema",
    # "AssocCategoryDiscountStrictSchema",
    # "AssocCustomerDiscountStrictSchema",
    # "AssocItemDiscountStrictSchema",
    # "AssocOrderItemStrictSchema",
    # "AssocOrderStatusStrictSchema",
    "CurrencyPlainSchema",
    "CurrencyStrictSchema",
    # "CustomerPlainSchema",
    # "CustomerStrictSchema",
    # "DiscountPlainSchema",
    # "DiscountStrictSchema",
    # "ExchangeRatePlainSchema",
    # "ExchangeRateStrictSchema",
    # "InvoicePlainSchema",
    # "InvoiceStrictSchema",
    # "OrderPlainSchema",
    # "OrderStrictSchema",
    # "PaymentMethodPlainSchema",
    # "PaymentMethodStrictSchema",
    # "StatusPlainSchema",
    # "StatusStrictSchema",
    # "SupplierPlainSchema",
    # "SupplierStrictSchema",
]
