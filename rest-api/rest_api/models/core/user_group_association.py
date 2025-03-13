from sqlalchemy import Column, Integer, ForeignKey
from config.database import Database
from models.base import Base, BaseModel


class UserGroupAssociation(BaseModel, Base):
    __tablename__ = "users_groups"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
