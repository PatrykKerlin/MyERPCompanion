from enum import IntEnum, StrEnum


class Module(IntEnum):
    CORE = 1
    MOBILE = 3


class ApiActionError(StrEnum):
    FETCH = "data_fetch_fail"
    SAVE = "record_save_fail"
    DELETE = "record_delete_fail"
    INVALID_CREDENTIALS = "invalid_credentials"


class View(StrEnum):
    CURRENT_USER = "current_user"
    USERS = "users"
    BINS = "bins"
    ITEMS = "items"
    BIN_TRANSFER = "bin_transfer"
    STOCK_RECEIVING = "stock_receiving"
    ORDER_PICKING = "order_picking"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    TRANSLATIONS_BY_LANGUAGE = "translations/by-language"
    TOKEN = "auth/token"
    REFRESH = "auth/refresh"
    CURRENT_USER = "current-user"
    MODULES = "modules"
    USERS = "users"
    LANGUAGES = "languages"
    WAREHOUSES_BY_USERNAME = "warehouses/by-username"
    BINS = "bins"
    BINS_GET_BULK = "bins/get-bulk"
    UNITS = "units"
    ITEMS = "items"
    ITEMS_GET_BULK = "items/get-bulk"
    BIN_ITEMS = "bin-items"
    BIN_ITEMS_CREATE_BULK = "bin-items/create-bulk"
    BIN_ITEMS_UPDATE_BULK = "bin-items/update-bulk"
    BIN_ITEMS_DELETE_BULK = "bin-items/delete-bulk"
    CATEGORIES = "categories"
    CUSTOMERS = "customers"
    ORDERS = "orders"
    ORDERS_PICKING_ELIGIBLE = "orders/picking-eligible"
    ORDERS_PICKING_SUMMARY = "orders/picking-summary"
    PURCHASE_ORDERS = "orders/purchase"
    ORDER_ITEMS = "order-items"
    ORDER_ITEMS_CREATE_BULK = "order-items/create-bulk"
    ORDER_ITEMS_UPDATE_BULK = "order-items/update-bulk"
    ORDER_STATUSES = "order-statuses"
    STATUSES = "statuses"
