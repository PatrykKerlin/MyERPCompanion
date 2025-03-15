from entities.base import Base, BaseEntity
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Group(BaseEntity, Base):
    __tablename__ = "groups"

    name = Column(String(10), unique=True, nullable=False)
    description = Column(String(255), nullable=False)

    users = relationship(
        "User",
        secondary="users_groups",
        primaryjoin="Group.id == users_groups.c.group_id",
        secondaryjoin="User.id == users_groups.c.user_id",
        back_populates="groups",
    )
