from pydantic import BaseModel


class TokenSchema(BaseModel):
    access: str
    refresh: str
