from enum import StrEnum


class ViewMode(StrEnum):
    SEARCH = "search"
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    LIST = "list"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    TRANSLATIONS_BY_LANGUAGE = "translations/by-language"
    TOKEN = "auth/token"
    REFRESH = "auth/refresh"
    CURRENT_USER = "current-user"
    MODULES = "modules"


class View(StrEnum):
    SIDE_MENU = "side_menu"
    CURRENT_USER = "current_user"
