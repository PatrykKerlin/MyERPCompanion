from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from entities.base import Base


class BaseEntity:
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    modified_at = Column(DateTime(timezone=True), onupdate=now(), nullable=True)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
