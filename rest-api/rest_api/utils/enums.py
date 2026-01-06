from enum import StrEnum


class Action(StrEnum):
    GET_ALL = "get_all"
    GET_ONE = "get_one"
    GET_MANY = "get_many"
    CREATE = "create"
    CREATE_MANY = "create_many"
    UPDATE = "update"
    UPDATE_MANY = "update_many"
    DELETE = "delete"
    DELETE_MANY = "delete_many"


class Permission(StrEnum):
    CAN_READ = "can_read"
    CAN_MODIFY = "can_modify"
