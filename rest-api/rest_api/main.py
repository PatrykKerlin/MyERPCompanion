from os import getenv

from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from config import Context, Database, Settings
from controllers import core
from handlers import DBCheck, PopulateSuperuser
from config import CustomFastAPI


class App:
    def __init__(
        self,
        settings: Settings,
        database: Database,
        oauth2_scheme: OAuth2PasswordBearer,
    ) -> None:
        self.__database = database
        self.__app = CustomFastAPI(title="MyERPCompanion API", redoc_url=None)
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
        # group_controller = core.GroupController(self.__context)

        api_router.include_router(health_check_controller.router, tags=["Health Check"])
        api_router.include_router(auth_controller.router, tags=["Authorization"])
        api_router.include_router(current_user_controller.router, tags=["Current User"])
        api_router.include_router(
            user_controller.router, prefix="/users", tags=["Users"]
        )
        # api_router.include_router(
        #     group_controller.router, prefix="/groups", tags=["Groups"]
        # )

        self.__app.include_router(api_router)

    async def startup(self) -> None:
        async with self.__database.engine.begin() as conn:
            await conn.run_sync(Database.get_base().metadata.create_all)

    def get_app(self) -> FastAPI:
        return self.__app


def create_app() -> FastAPI:
    settings = Settings(
        DATABASE_URL=getenv("DATABASE_URL", ""),
        SECRET_KEY=getenv("SECRET_KEY", "")
    )
    database = Database(settings)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")
    app_instance = App(settings, database, oauth2_scheme)
    app = app_instance.get_app()

    @app.on_event("startup")
    async def on_startup() -> None:
        await DBCheck(database.get_db).wait_for_db()
        await PopulateSuperuser(database.get_db).populate_superuser()
        await app_instance.startup()

    return app


start_app = create_app()
