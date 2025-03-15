from config.database import Database
from entities.base import Base, BaseEntity
from sqlalchemy import Column, ForeignKey, Integer


class UserGroupAssociation(BaseEntity, Base):
    __tablename__ = "users_groups"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
