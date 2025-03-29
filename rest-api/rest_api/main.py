from contextlib import asynccontextmanager
from os import getenv
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.security import OAuth2PasswordBearer

from config import Context, CustomFastAPI, Database, Settings
from controllers import core
from handlers import DBCheck, PopulateSuperuser
from services.core import AuthService
from middlewares import AuthMiddleware


class App:
    def __init__(
        self,
        settings: Settings,
        database: Database,
        oauth2_scheme: OAuth2PasswordBearer,
        lifespan: Any = None,
    ) -> None:
        self.__database = database
        self.__app = CustomFastAPI(
            title="MyERPCompanion API",
            redoc_url=None,
            lifespan=lifespan,
        )
        self.__context = Context(
            get_db=self.__database.get_db,
            settings=settings,
            oauth2_scheme=oauth2_scheme,
        )
        self.__include_routers()

    def __include_routers(self) -> None:
        api_router = APIRouter(prefix="/api")

        health_check_controller = core.HealthCheckController()
        auth_controller = core.AuthController(self.__context)
        current_user_controller = core.CurrentUserController(self.__context)
        user_controller = core.UserController(self.__context)
        group_controller = core.GroupController(self.__context)

        api_router.include_router(health_check_controller.router, tags=["Health Check"])
        api_router.include_router(auth_controller.router, tags=["Authorization"])
        api_router.include_router(current_user_controller.router, tags=["Current User"])
        api_router.include_router(
            user_controller.router, prefix="/users", tags=["Users"]
        )
        api_router.include_router(
            group_controller.router, prefix="/groups", tags=["Groups"]
        )

        self.__app.include_router(api_router)

    async def startup(self) -> None:
        async with self.__database.engine.begin() as conn:
            await conn.run_sync(Database.get_base().metadata.create_all)

    def get_app(self) -> FastAPI:
        return self.__app


def create_app() -> FastAPI:
    settings = Settings(
        DATABASE_URL=getenv("DATABASE_URL", ""), SECRET_KEY=getenv("SECRET_KEY", "")
    )
    database = Database(settings)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await DBCheck(database.get_db).wait_for_db()
        await app_instance.startup()
        await PopulateSuperuser(database.get_db).populate_superuser()
        yield

    app_instance = App(settings, database, oauth2_scheme, lifespan=lifespan)

    AuthService.set_settings(settings)
    app_instance.get_app().add_middleware(AuthMiddleware)

    return app_instance.get_app()


start_app = create_app()
