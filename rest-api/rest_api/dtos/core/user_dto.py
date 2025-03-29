from datetime import datetime
from typing import List

from pydantic import PrivateAttr

from dtos.base import BaseDTO


class UserDTO(BaseDTO):
    username: str
    groups: list["GroupDTO"]
    is_superuser: bool | None = None
    password: str | None = PrivateAttr(default=None)
    pwd_modified_at: datetime | None = None
