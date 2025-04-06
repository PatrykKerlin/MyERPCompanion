import importlib
from typing import Generic, TypeVar, cast

from fastapi import APIRouter, FastAPI
from sqlalchemy import select
from sqlalchemy.sql.elements import BinaryExpression

from config import Context
from controllers.base import BaseController
from entities.core import Endpoint

TController = TypeVar("TController", bound=BaseController)


class RegisterDynamicEndpoints(Generic[TController]):
    def __init__(self, context: Context, app: FastAPI) -> None:
        self.__context = context
        self.__app = app
        self.__api_router = APIRouter(prefix="/api")

    @classmethod
    def _import_controller(cls, controller_name: str) -> type[TController]:
        endpoint = importlib.import_module("controllers.core")
        return getattr(endpoint, controller_name)

    async def register(self) -> None:
        async with self.__context.get_session() as db:
            query = select(Endpoint).where(
                cast(BinaryExpression, Endpoint.is_active == True)
            )
            result = await db.execute(query)
            endpoints = result.scalars().all()

            for endpoint in endpoints:
                try:
                    controller_class = self._import_controller(endpoint.controller)
                    controller = controller_class(self.__context)
                    self.__api_router.include_router(
                        controller.router,
                        prefix=endpoint.path,
                        tags=[endpoint.tag],
                    )
                except Exception as e:
                    print(f"Failed to load controller: {endpoint.controller}: {e}")

        self.__app.include_router(self.__api_router)
