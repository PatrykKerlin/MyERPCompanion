from typing import List
from models.core import User, Group


class UserDTO:
    def __init__(self, id: int, username: str, groups: List[Group]) -> None:
        self.id = id
        self.username = username
        self.groups = groups

    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        return cls(id=user.id, username=user.username, groups=user.groups)
