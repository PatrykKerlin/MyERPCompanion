from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .module import Module


class Endpoint(BaseModel):
    __tablename__ = "endpoints"

    controller: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String(25), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(25), nullable=True)

    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    module: Mapped["Module"] = relationship(argument="Module", back_populates="endpoints", foreign_keys=[module_id])
