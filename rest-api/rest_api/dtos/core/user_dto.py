from typing import List

from dtos.base import BaseDTO
from entities.core import Group, User


class UserDTO(BaseDTO):
    def __init__(
        self, id: int, username: str, groups: List[Group], is_superuser: bool, password: str | None = None
    ) -> None:
        super().__init__(id)
        self.username = username
        self.__password = password
        self.groups = groups
        self.__is_superuser = is_superuser

    @property
    def is_superuser(self) -> bool:
        return self.__is_superuser

    @property
    def password(self) -> str | None:
        password = self.__password
        self.__password = None
        return password

    @password.deleter
    def password(self) -> None:
        self.__password = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, username={self.username}, "
            f"groups={self.groups}, is_superuser={self.__is_superuser})"
        )
