from schemas.core import TokenSchema
from services.base import BaseService


class AuthService(BaseService):
    async def fetch_token(self, username: str, password: str) -> TokenSchema:
        response = await self._post("/auth", {"username": username, "password": password})
        return TokenSchema(**response.json())
