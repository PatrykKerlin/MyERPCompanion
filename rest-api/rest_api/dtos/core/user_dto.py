from datetime import datetime
from typing import Union, Any
from pydantic import PrivateAttr

from dtos.base import BaseDTO
from schemas.core import UserCreate, UserUpdate
from entities.core import User


class UserDTO(BaseDTO):
    username: str
    groups: list["GroupDTO"]
    pwd_modified_at: datetime | None = None

    __password: str | None = PrivateAttr(default=None)
    __is_superuser: bool | None = PrivateAttr(default=None)

    @property
    def password(self) -> str | None:
        return self.__password

    @password.setter
    def password(self, value: str | None) -> None:
        self.__password = value

    @property
    def is_superuser(self) -> bool | None:
        return self.__is_superuser

    @is_superuser.setter
    def is_superuser(self, value: bool | None) -> None:
        self.__is_superuser = value

    @classmethod
    def from_schema(cls, schema: Union["UserCreate", "UserUpdate", dict[str, Any]]) -> "UserDTO":
        dto = super().from_schema(schema)

        if isinstance(schema, dict):
            dto.password = schema.get("password")
            dto.is_superuser = schema.get("is_superuser")
        else:
            dto.password = getattr(schema, "password", None)
            dto.is_superuser = getattr(schema, "is_superuser", None)

        return dto

    @classmethod
    def from_entity(cls, entity: User) -> "UserDTO":
        dto = super().from_entity(entity)
        dto.is_superuser = entity.is_superuser
        return dto

    def to_entity(self, entity_cls: type[User]) -> User:
        entity_data = self.model_dump(exclude_unset=True)
        if self.password is not None:
            entity_data["password"] = self.password
        if self.is_superuser is not None:
            entity_data["is_superuser"] = self.is_superuser
        return entity_cls(**entity_data)
