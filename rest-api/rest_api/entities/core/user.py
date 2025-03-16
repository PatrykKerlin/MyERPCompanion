from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from entities.base import Base, BaseEntity


class User(BaseEntity, Base):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    groups = relationship(
        "Group",
        secondary="users_groups",
        primaryjoin="User.id == users_groups.c.user_id",
        secondaryjoin="Group.id == users_groups.c.group_id",
        back_populates="users",
    )
