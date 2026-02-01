from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as base_relationship
from sqlalchemy.orm.relationships import (
    _LazyLoadArgumentType,
    _ORMColCollectionArgument,
    _RelationshipArgumentType,
    _RelationshipDeclared,
)


class Fields:
    @staticmethod
    def foreign_key(
        column: str, nullable: bool = False, unique: bool = False, primary_key: bool = False
    ) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey(column), nullable=nullable, unique=unique, primary_key=primary_key)

    @staticmethod
    def relationship(
        argument: _RelationshipArgumentType[Any],
        back_populates: str | None,
        foreign_keys: _ORMColCollectionArgument,
        uselist: bool = True,
        lazy: _LazyLoadArgumentType = "select",
        cascade_soft_delete: bool = False,
        **kwargs: Any,
    ) -> _RelationshipDeclared[Any]:
        info = kwargs.pop("info", {}) or {}
        info["cascade_soft_delete"] = cascade_soft_delete
        return base_relationship(
            argument=argument,
            back_populates=back_populates,
            foreign_keys=foreign_keys,
            uselist=uselist,
            lazy=lazy,
            info=info,
            **kwargs,
        )

    @staticmethod
    def id() -> Mapped[int]:
        return mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    @staticmethod
    def is_active() -> Mapped[bool]:
        return mapped_column(Boolean, default=True, nullable=False)

    @staticmethod
    def created_at() -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    @staticmethod
    def created_by() -> Mapped[int | None]:
        return mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @staticmethod
    def modified_at() -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    @staticmethod
    def modified_by() -> Mapped[int | None]:
        return mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @staticmethod
    def key(unique: bool = True) -> Mapped[str]:
        return mapped_column(String(25), nullable=False, unique=unique)

    @staticmethod
    def name(unique: bool = True) -> Mapped[str]:
        return mapped_column(String(50), nullable=False, unique=unique)

    @staticmethod
    def boolean(default: bool) -> Mapped[bool]:
        return mapped_column(Boolean, nullable=False, default=default)

    @staticmethod
    def date(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Date, nullable=nullable)

    @staticmethod
    def datetime(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(DateTime, nullable=nullable)

    @staticmethod
    def integer(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(Integer, nullable=nullable, unique=unique)

    @staticmethod
    def numeric_3_2(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Numeric(3, 2), nullable=nullable)

    @staticmethod
    def numeric_4_3(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Numeric(4, 3), nullable=nullable)

    @staticmethod
    def numeric_10_2(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Numeric(10, 2), nullable=nullable)

    @staticmethod
    def numeric_6_3(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Numeric(7, 3), nullable=nullable)

    @staticmethod
    def numeric_11_3(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(Numeric(11, 3), nullable=nullable)

    @staticmethod
    def string_10(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(String(10), nullable=nullable, unique=unique)

    @staticmethod
    def string_20(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(String(20), nullable=nullable, unique=unique)

    @staticmethod
    def string_50(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(String(50), nullable=nullable, unique=unique)

    @staticmethod
    def string_100(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(String(100), nullable=nullable, unique=unique)

    @staticmethod
    def string_1000(nullable: bool = False, unique: bool = False) -> Mapped[Any]:
        return mapped_column(String(1000), nullable=nullable, unique=unique)

    @staticmethod
    def string_list(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(ARRAY(String(50)), nullable=nullable)

    @staticmethod
    def bank_account() -> Mapped[str]:
        return mapped_column(String(28), nullable=False)

    @staticmethod
    def bank_swift() -> Mapped[str]:
        return mapped_column(String(11), nullable=False)

    @staticmethod
    def ean() -> Mapped[str]:
        return mapped_column(String(13), nullable=False, unique=True)

    @staticmethod
    def id_document(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(String(9), nullable=nullable, unique=True)

    @staticmethod
    def pesel() -> Mapped[str | None]:
        return mapped_column(String(11), nullable=True, unique=True)

    @staticmethod
    def postal_code(nullable: bool = False) -> Mapped[Any]:
        return mapped_column(String(6), nullable=nullable)

    @staticmethod
    def symbol() -> Mapped[str]:
        return mapped_column(String(3), nullable=False, unique=True)
