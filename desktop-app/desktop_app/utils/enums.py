from enum import StrEnum


class ViewMode(StrEnum):
    SEARCH = "search"
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    LIST = "list"


class View(StrEnum):
    SIDE_MENU = "side_menu"
    CURRENT_USER = "current_user"
    DEPARTMENTS = "departments"
    POSITIONS = "positions"
    EMPLOYEES = "employees"


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
