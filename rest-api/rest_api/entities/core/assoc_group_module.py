from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from entities.base import BaseEntity


class AssocGroupModule(BaseEntity):
    __tablename__ = "groups_modules"

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), primary_key=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id"), primary_key=True)
