from enum import StrEnum


class Action(StrEnum):
    GET_ALL = "get_all"
    GET_ONE = "get_one"
    GET_MANY = "get_many"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Permission(StrEnum):
    CAN_READ = "can_read"
    CAN_MODIFY = "can_modify"
