from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .setting_key import SettingKey
    from .text import Text
    from .user import User


class Setting(BaseEntity):
    __tablename__ = "settings"

    value: Mapped[str] = mapped_column(String(25), nullable=False)

    key_id: Mapped[int] = mapped_column(ForeignKey("settings_keys.id"), nullable=False)

    key: Mapped["SettingKey"] = relationship(
        argument="SettingKey",
        back_populates="values",
        foreign_keys=[key_id],
        lazy="selectin",
    )
    user_languages: Mapped[list["User"]] = relationship(
        argument="User",
        back_populates="language",
        foreign_keys="User.language_id",
        lazy="selectin",
    )
    user_themes: Mapped[list["User"]] = relationship(
        argument="User",
        back_populates="theme",
        foreign_keys="User.theme_id",
        lazy="selectin",
    )
    text_languages: Mapped[list["Text"]] = relationship(
        argument="Text",
        back_populates="language",
        foreign_keys="Text.language_id",
        lazy="selectin",
    )
