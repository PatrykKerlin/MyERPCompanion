from schemas.core import TokenInputSchema, UserInputSchema
from services.base import BaseService


class AuthService(BaseService):
    async def fetch_tokens(self, username: str, password: str) -> TokenInputSchema:
        response = await self._post("/auth", {"username": username, "password": password})
        return TokenInputSchema(**response.json())

    async def fetch_current_user(self) -> UserInputSchema:
        response = await self._get("/current-user")
        return UserInputSchema(**response.json())
