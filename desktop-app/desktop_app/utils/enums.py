from enum import StrEnum, IntEnum


class ViewMode(StrEnum):
    NONE = "none"
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
    DELIVERY_METHODS = "delivery_methods"
    UNITS = "units"
    ITEMS = "items"
    BIN_TRANSFER = "bin_transfer"
    SUPPLIERS = "suppliers"
    CATEGORIES = "categories"
    DISCOUNTS = "discounts"
    CURRENCIES = "currencies"


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
    BINS_GET_BULK = "bins/get-bulk"
    CARRIERS = "carriers"
    DELIVERY_METHODS = "delivery-methods"
    UNITS = "units"
    ITEMS = "items"
    ITEMS_GET_BULK = "items/get-bulk"
    BIN_ITEMS = "bin-items"
    BIN_ITEMS_GET_BULK = "bin-items/get-bulk"
    BIN_ITEMS_CREATE_BULK = "bin-items/create-bulk"
    BIN_ITEMS_UPDATE_BULK = "bin-items/update-bulk"
    BIN_ITEMS_DELETE_BULK = "bin-items/delete-bulk"
    SUPPLIERS = "suppliers"
    CATEGORIES = "categories"
    IMAGES = "images"
    IMAGES_UPDATE_BULK = "images/update-bulk"
    DISCOUNTS = "discounts"
    DISCOUNTS_GET_BULK = "discounts/get-bulk"
