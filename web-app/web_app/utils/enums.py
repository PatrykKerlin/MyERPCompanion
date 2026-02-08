from enum import IntEnum, StrEnum


class ViewMode(StrEnum):
    NONE = "none"
    STATIC = "static"


class Module(IntEnum):
    CORE = 1
    WEB = 2


class ApiActionError(StrEnum):
    FETCH = "data_fetch_fail"
    SAVE = "record_save_fail"
    INVALID_CREDENTIALS = "invalid_credentials"


class View(StrEnum):
    WEB_CREATE_ORDER = "web_create_order"
    WEB_ORDERS = "web_orders"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    TRANSLATIONS_BY_LANGUAGE = "translations/by-language"
    TOKEN = "auth/token"
    REFRESH = "auth/refresh"
    CURRENT_USER = "current-user"
    MODULES = "modules"
    USERS = "users"
    LANGUAGES = "languages"
    ITEMS = "items"
    ORDERS = "orders"
    SALES_ORDERS = "orders/sales"
    ORDER_VIEW_SALES = "orders/view/sales"
    ORDER_ITEMS_CREATE_BULK = "order-items/create-bulk"
    ORDER_STATUSES_CREATE_BULK = "order-statuses/create-bulk"
