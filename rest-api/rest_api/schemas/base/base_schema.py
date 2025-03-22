from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


class BaseCreateSchema(BaseSchema):
    pass


class BaseUpdateSchema(BaseSchema):
    pass


class BaseResponseSchema(BaseSchema):
    id: int
