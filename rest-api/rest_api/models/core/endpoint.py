from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .module import Module


class Endpoint(BaseModel):
    __tablename__ = "endpoints"

    key: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    controller: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    path: Mapped[str] = mapped_column(String(100), nullable=False)
    in_menu: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    order: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)

    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=True)
    module: Mapped[Module] = relationship(argument="Module", back_populates="endpoints", foreign_keys=[module_id])
