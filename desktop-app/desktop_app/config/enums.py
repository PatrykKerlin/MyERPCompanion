from enum import StrEnum


class TextKey(StrEnum):
    API_NOT_RESPONDING = "API is not responding."


class ViewMode(StrEnum):
    SEARCH = "search"
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    LIST = "list"


class Endpoint(StrEnum):
    HEALTH_CHECK = "health-check"
    REFRESH = "refresh"
    TEXTS_BY_LANGUAGE = "texts/by-language"
