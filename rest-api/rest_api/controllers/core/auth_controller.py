from config import Settings
from fastapi import APIRouter, HTTPException, status
from schemas.core import AuthSchema
from services.core import AuthService


class AuthController:
    def __init__(self, get_db, settings: Settings):
        self.__get_db = get_db
        self.__settings = settings
        self.router = APIRouter()
        self.router.add_api_route("/auth", self.auth, methods=["POST"])

    async def auth(self, auth: AuthSchema) -> dict:
        async with self.__get_db() as db:
            token = await AuthService.authenticate(
                db, auth.username, auth.password, self.__settings
            )
            if not token:
                raise HTTPException(
                    status_code=status.status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
            return {"token": token}
