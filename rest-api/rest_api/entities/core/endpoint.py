from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .module import Module


class Endpoint(BaseEntity):
    __tablename__ = "endpoints"

    controller: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String(25), nullable=False)
    tag: Mapped[str] = mapped_column(String(25), nullable=True)

    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship(back_populates="endpoints", lazy="selectin")
