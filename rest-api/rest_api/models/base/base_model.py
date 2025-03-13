from sqlalchemy import Column, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from sqlalchemy.ext.declarative import declared_attr
from models.base import Base


class BaseModel:
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    modified_at = Column(DateTime(timezone=True), onupdate=now(), nullable=True)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # @classmethod
    # @declared_attr
    # def creator(cls):
    #     return relationship("User", remote_side=[cls.id], foreign_keys=[cls.created_by], uselist=False)
    #
    # @classmethod
    # @declared_attr
    # def modifier(cls):
    #     return relationship("User", remote_side=[cls.id], foreign_keys=[cls.modified_by], uselist=False)
