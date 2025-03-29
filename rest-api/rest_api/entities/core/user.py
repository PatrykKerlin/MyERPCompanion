from datetime import datetime
from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from entities.base import BaseEntity


class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    pwd_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=now())

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="users_groups",
        primaryjoin="User.id == users_groups.c.user_id",
        secondaryjoin="Group.id == users_groups.c.group_id",
        back_populates="users",
    )
