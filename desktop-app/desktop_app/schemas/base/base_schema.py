from __future__ import annotations

from datetime import datetime

from typing import Annotated

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class BasePlainSchema(BaseSchema):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    modified_at: datetime | None = None
    modified_by: int | None = None

    created_by_username: str | None = None
    modified_by_username: str | None = None


class BaseStrictSchema(BaseSchema):
    id: Annotated[int | None, Field(ge=1, exclude=True)] = None
