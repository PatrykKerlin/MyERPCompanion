from fastapi import APIRouter, HTTPException, status

from config import Context, Settings
from schemas.core import AuthSchema
from services.core import AuthService


class AuthController:
    def __init__(self, context: Context):
        self.__context = context
        self.router = APIRouter()
        self.router.add_api_route("/auth", self.auth, methods=["POST"])

    async def auth(self, auth: AuthSchema) -> dict:
        async with self.__context.get_db() as db:
            token = await AuthService.authenticate(
                db, auth.username, auth.password, self.__context.settings
            )
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
            return {"token": token}
