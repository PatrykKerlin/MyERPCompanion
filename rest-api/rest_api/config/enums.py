from enum import StrEnum


class Action(StrEnum):
    GET_ALL = "get_all"
    GET_ONE = "get_one"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Permission(StrEnum):
    CAN_LIST = "can_list"
    CAN_SHOW = "can_show"
    CAN_CREATE = "can_create"
    CAN_UPDATE = "can_update"
    CAN_DELETE = "can_delete"
