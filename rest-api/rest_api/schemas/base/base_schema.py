from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


class BaseCreateSchema(BaseSchema):
    pass


class BaseResponseSchema(BaseSchema):
    id: int = Field(...)
