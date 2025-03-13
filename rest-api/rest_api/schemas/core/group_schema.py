from pydantic import BaseModel, Field, constr


class GroupCreate(BaseModel):
    name: constr(min_length=1, max_length=10) = Field(...)
    description: constr(min_length=1, max_length=255) = Field(...)

    class Config:
        from_attributes = True


class GroupOut(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    description: str = Field(...)

    class Config:
        from_attributes = True
