from enum import StrEnum, IntEnum


class ViewMode(StrEnum):
    SEARCH = "search"
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    LIST = "list"
    STATIC = "static"


class Module(IntEnum):
    CORE = 1


class View(StrEnum):
    SIDE_MENU = "side_menu"
    CURRENT_USER = "current_user"
    DEPARTMENTS = "departments"
    POSITIONS = "positions"
    EMPLOYEES = "employees"
    WAREHOUSES = "warehouses"
    BINS = "bins"
    CARRIERS = "carriers"
    DELIVERY_METHODS = "delivery-methods"
    UNITS = "units"
    ITEMS = "items"
    BIN_TRANSFER = "bin_transfer"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    TRANSLATIONS_BY_LANGUAGE = "translations/by-language"
    TOKEN = "auth/token"
    REFRESH = "auth/refresh"
    CURRENT_USER = "current-user"
    MODULES = "modules"
    USERS = "users"
    DEPARTMENTS = "departments"
    POSITIONS = "positions"
    CURRENCIES = "currencies"
    EMPLOYEES = "employees"
    WAREHOUSES = "warehouses"
    BINS = "bins"
    CARRIERS = "carriers"
    DELIVERY_METHODS = "delivery-methods"
    UNITS = "units"
    ITEMS = "items"
    BIN_ITEMS = "bin-items"
