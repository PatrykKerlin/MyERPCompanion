from enum import StrEnum


class ViewMode(StrEnum):
    SEARCH = "search"
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    LIST = "list"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    REFRESH = "refresh"
    TRANSLATIONS_BY_LANGUAGE = "translations/by-language"
