from __future__ import annotations

from pydantic import model_validator
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocModuleGroupStrictSchema(BaseStrictSchema):
    can_read: Constraints.BooleanTrue
    can_modify: Constraints.BooleanFalse
    group_id: Constraints.PositiveInteger
    module_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def validate_data(self) -> AssocModuleGroupStrictSchema:
        if self.can_modify and not self.can_read:
            raise ValueError("can_read is required for can_modify")
        if not self.can_read and not self.can_modify:
            raise ValueError("at least one permission must be granted")
        return self


class AssocModuleGroupPlainSchema(BasePlainSchema):
    can_read: bool
    can_modify: bool
    group_id: int
    module_id: int
