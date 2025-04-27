from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class BaseInputSchema(BaseSchema):
    pass


class BaseOutputSchema(BaseSchema):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    modified_at: datetime | None
    modified_by: int | None
