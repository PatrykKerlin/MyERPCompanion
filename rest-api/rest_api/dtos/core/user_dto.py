from typing import List

from dtos.base import BaseDTO
from entities.core import Group, User


class UserDTO(BaseDTO):
    def __init__(
        self, id: int, username: str, is_superuser: bool, groups: List[Group]
    ) -> None:
        super().__init__(id)
        self.username = username
        self.groups = groups
        self.__is_superuser = is_superuser

    @property
    def is_superuser(self) -> bool:
        return self.__is_superuser
