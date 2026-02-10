from enum import StrEnum


class Action(StrEnum):
    GET_ALL = "get_all"
    GET_ONE = "get_one"
    GET_BULK = "get_bulk"
    CREATE = "create"
    CREATE_BULK = "create_bulk"
    UPDATE = "update"
    UPDATE_BULK = "update_bulk"
    DELETE = "delete"
    DELETE_BULK = "delete_bulk"


class Permission(StrEnum):
    CAN_READ = "can_read"
    CAN_MODIFY = "can_modify"
