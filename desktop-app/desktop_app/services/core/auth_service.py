from schemas.core import TokenPlainSchema, UserPlainSchema
from services.base import BaseService


class AuthService(BaseService):
    async def fetch_tokens(self, username: str, password: str) -> TokenPlainSchema:
        response = await self._post("/auth", {"username": username, "password": password})
        return TokenPlainSchema(**response.json())

    async def fetch_current_user(self) -> UserPlainSchema:
        response = await self._get("/current-user")
        return UserPlainSchema(**response.json())
