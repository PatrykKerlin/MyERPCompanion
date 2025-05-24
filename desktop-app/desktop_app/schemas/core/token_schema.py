from pydantic import BaseModel


class TokenInputSchema(BaseModel):
    access: str
    refresh: str
