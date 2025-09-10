from enum import StrEnum


class Action(StrEnum):
    GET_ALL = "get_all"
    GET_ONE = "get_one"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Permission(StrEnum):
    CAN_READ = "can_read"
    CAN_MODIFY = "can_modify"
