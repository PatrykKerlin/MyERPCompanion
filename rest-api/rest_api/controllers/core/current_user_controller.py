from fastapi import APIRouter, Request, status, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from schemas.core import UserPlainSchema
from utils.auth import Auth


class CurrentUserController:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserPlainSchema,
            status_code=status.HTTP_200_OK,
        )

    @Auth.restrict_access()
    async def current_user(self, request: Request) -> UserPlainSchema:
        try:
            user = request.state.user
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return UserPlainSchema.model_validate(user)
        except HTTPException:
            raise
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
