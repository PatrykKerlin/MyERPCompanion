from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from entities.base import BaseEntity


class UserGroupAssociation(BaseEntity):
    __tablename__ = "users_groups"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id"), primary_key=True
    )
