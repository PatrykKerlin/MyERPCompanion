from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .setting import Setting


class SettingKey(BaseModel):
    __tablename__ = "settings_keys"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    values: Mapped[list["Setting"]] = relationship(
        argument="Setting",
        back_populates="key",
        foreign_keys="Setting.key_id",
    )
