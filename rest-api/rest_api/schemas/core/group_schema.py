from typing import Annotated

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=10)]
    description: Annotated[str, Field(min_length=1, max_length=255)]

    class Config:
        from_attributes = True


class GroupOut(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    description: str = Field(...)

    class Config:
        from_attributes = True
