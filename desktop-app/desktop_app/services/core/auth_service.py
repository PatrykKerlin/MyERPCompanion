import httpx
from schemas.core import TokenSchema


class AuthService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def login(self, username: str, password: str) -> TokenSchema:
        response = httpx.post(f"{self.base_url}/auth", json={"username": username, "password": password})
        response.raise_for_status()
        data = response.json()
        return TokenSchema(**data)
