from fastapi import APIRouter, Request, status
from utils.auth import Auth
from utils.exceptions import InvalidCredentialsException
from schemas.core import UserOutputSchema


class CurrentUserController:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserOutputSchema,
            status_code=status.HTTP_200_OK,
        )

    @Auth.restrict_access()
    async def current_user(self, request: Request) -> UserOutputSchema:
        user = request.state.user
        if not user:
            raise InvalidCredentialsException()
        return UserOutputSchema.model_construct(**user.model_dump())
