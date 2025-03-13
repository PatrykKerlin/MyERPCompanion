from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base, BaseModel


class User(BaseModel, Base):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    groups = relationship(
        "Group",
        secondary="users_groups",
        primaryjoin="User.id == users_groups.c.user_id",
        secondaryjoin="Group.id == users_groups.c.group_id",
        back_populates="users"
    )
