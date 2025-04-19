from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class BaseCreateSchema(BaseSchema):
    pass


class BaseResponseSchema(BaseSchema):
    id: int


class BaseInternalSchema(BaseResponseSchema):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    modified_at: datetime | None = None
    modified_by: int | None = None
