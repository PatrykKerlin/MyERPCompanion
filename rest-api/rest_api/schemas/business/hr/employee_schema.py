from __future__ import annotations

from datetime import date
from typing import Annotated, TYPE_CHECKING

from pydantic import Field, model_validator, EmailStr, ValidationInfo

from schemas.base import BaseStrictSchema, BasePlainSchema

if TYPE_CHECKING:
    from ...core.user_schema import UserPlainSchema
    from .department_schema import DepartmentPlainSchema
    from .position_schema import PositionPlainSchema


class EmployeeStrictSchema(BaseStrictSchema):
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    middle_name: Annotated[str | None, Field(max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]

    pesel: Annotated[str | None, Field(min_length=11, max_length=11)]
    birth_date: date
    birth_place: Annotated[str, Field(min_length=1, max_length=50)]

    passport_number: Annotated[str | None, Field(min_length=9, max_length=9)]
    passport_expiry: date | None
    id_card_number: Annotated[str | None, Field(min_length=9, max_length=9)]
    id_card_expiry: date | None

    email: Annotated[EmailStr | None, Field(max_length=100)]
    phone_number: Annotated[str | None, Field(pattern=r"^[0-9+\-\s]+$", min_length=9, max_length=25)]

    hire_date: date
    termination_date: date | None
    salary: Annotated[int, Field(ge=1)]

    street: Annotated[str | None, Field(max_length=50)]
    house_number: Annotated[str, Field(min_length=1, max_length=10)]
    apartment_number: Annotated[str | None, Field(max_length=10)]
    postal_code: Annotated[str, Field(pattern=r"^\d{2}-\d{3}$", min_length=6, max_length=6)]
    city: Annotated[str, Field(min_length=1, max_length=50)]
    country: Annotated[str, Field(min_length=1, max_length=50)]

    bank_account: Annotated[str, Field(pattern=r"^\d+$", min_length=26, max_length=26)]
    bank_name: Annotated[str, Field(min_length=1, max_length=50)]

    manager_id: Annotated[int | None, Field(ge=1)]
    position_id: Annotated[int, Field(ge=1)]
    department_id: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def _validate_data(self, info: ValidationInfo) -> EmployeeStrictSchema:
        today = date.today()

        if bool(self.passport_number) ^ bool(self.passport_expiry):
            raise ValueError("passport_number and passport_expiry must be both set or both null")
        if bool(self.id_card_number) ^ bool(self.id_card_expiry):
            raise ValueError("id_card_number and id_card_expiry must be both set or both null")
        if not self.id_card_number and not self.passport_number:
            raise ValueError("at least one document is required: id_card_number or passport_number")

        if self.birth_date > today:
            raise ValueError("birth_date cannot be in the future")
        if self.hire_date < self.birth_date:
            raise ValueError("hire_date cannot be earlier than birth_date")
        if self.termination_date is not None and self.termination_date < self.hire_date:
            raise ValueError("termination_date cannot be earlier than hire_date")

        if self.passport_expiry is not None and self.passport_expiry < today:
            raise ValueError("passport_expiry must be today or later")
        if self.id_card_expiry is not None and self.id_card_expiry < today:
            raise ValueError("id_card_expiry must be today or later")

        rng = info.context.get("position_salary_range") if info.context else None
        if rng is not None:
            min_salary, max_salary = rng
            if self.salary < min_salary or self.salary > max_salary:
                raise ValueError(f"salary must be between {min_salary} and {max_salary} for the given position")

        return self


class EmployeePlainSchema(BasePlainSchema):
    first_name: str
    middle_name: str | None
    last_name: str

    pesel: str | None
    birth_date: date
    birth_place: str

    passport_number: str | None
    passport_expiry: date | None
    id_card_number: str | None
    id_card_expiry: date | None

    email: str
    phone_number: str | None

    hire_date: date
    termination_date: date | None
    salary: int

    street: str | None
    house_number: str
    apartment_number: str | None
    postal_code: str
    city: str
    country: str

    bank_account: str
    bank_name: str

    manager_id: int | None
    subordinates: list[int] = Field(default_factory=list)

    position: PositionPlainSchema
    department: DepartmentPlainSchema
    user: UserPlainSchema | None
