from dtos.base import BaseDTO


class GroupDTO(BaseDTO):
    name: str
    description: str
    users: list["UserDTO"] | None = None
