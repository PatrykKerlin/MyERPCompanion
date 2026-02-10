from __future__ import annotations

from datetime import date

from pydantic import ValidationInfo, model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class EmployeeStrictSchema(BaseStrictSchema):
    first_name: Constraints.String_50
    middle_name: Constraints.StringOptional_50
    last_name: Constraints.String_50

    pesel: Constraints.PeselOptional
    birth_date: date
    birth_place: Constraints.String_50

    passport_number: Constraints.IdDocumentOptional
    passport_expiry: date | None
    id_card_number: Constraints.IdDocumentOptional
    id_card_expiry: date | None

    email: Constraints.EmailOptional
    phone_number: Constraints.PhoneNumber

    street: Constraints.StringOptional_50
    house_number: Constraints.String_10
    apartment_number: Constraints.StringOptional_10
    postal_code: Constraints.PostalCode
    city: Constraints.String_50
    country: Constraints.String_50

    hire_date: date
    termination_date: date | None
    salary: Constraints.PositiveInteger
    is_remote: Constraints.BooleanFalse

    bank_account: Constraints.BankAccount
    bank_swift: Constraints.BankSwift
    bank_name: Constraints.String_50

    manager_id: Constraints.PositiveIntegerOptional
    department_id: Constraints.PositiveInteger
    position_id: Constraints.PositiveInteger

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
        if self.termination_date and self.termination_date < self.hire_date:
            raise ValueError("termination_date cannot be earlier than hire_date")

        if self.passport_expiry and self.passport_expiry < today:
            raise ValueError("passport_expiry must be today or later")
        if self.id_card_expiry and self.id_card_expiry < today:
            raise ValueError("id_card_expiry must be today or later")

        salary_range = info.context.get("salary_range") if info.context else None
        if salary_range is not None:
            min_salary, max_salary = salary_range
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

    email: str | None
    phone_number: str

    hire_date: date
    termination_date: date | None
    salary: int
    is_remote: bool

    street: str | None
    house_number: str
    apartment_number: str | None
    postal_code: str
    city: str
    country: str

    bank_account: str
    bank_swift: str
    bank_name: str

    manager_id: int | None

    position_id: int
    department_id: int
    user_id: int | None

    subordinate_ids: list[int]
