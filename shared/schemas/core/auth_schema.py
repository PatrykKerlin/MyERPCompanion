from schemas.base import BaseStrictSchema, Constraints


class AuthStrictSchema(BaseStrictSchema):
    username: Constraints.Username
    password: Constraints.Password
