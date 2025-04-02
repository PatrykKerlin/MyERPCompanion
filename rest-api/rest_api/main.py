from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import APIRouter, FastAPI

from config import Context, CustomFastAPI, Database, Settings
from controllers.core import AuthController, EndpointController, HealthCheckController
from handlers import CheckDatabaseState, PopulateDatabase, RegisterDynamicEndpoints
from middlewares import AuthMiddleware


class App:
    def __init__(
        self,
        settings: Settings,
        database: Database,
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
            settings=settings
        )
        self.__include_routers()

    def __include_routers(self) -> None:
        api_router = APIRouter(prefix="/api")

        health_check_controller = HealthCheckController()
        auth_controller = AuthController(self.__context)
        endpoint_controller = EndpointController(self.__context)

        api_router.include_router(health_check_controller.router, tags=["Health Check"])
        api_router.include_router(auth_controller.router, tags=["Authorization"])
        api_router.include_router(endpoint_controller.router, prefix="/endpoints", tags=["Endpoints"])

        self.__app.include_router(api_router)

    async def register_dynamic_endpoints(self) -> None:
        await RegisterDynamicEndpoints(self.__context, self.__app).register()

    async def startup(self) -> None:
        async with self.__database.engine.begin() as conn:
            await conn.run_sync(Database.get_base().metadata.create_all)

    def get_app(self) -> FastAPI:
        return self.__app


def create_app() -> FastAPI:
    settings = Settings()  # type: ignore
    database = Database(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        populate = PopulateDatabase(database.get_db)
        await CheckDatabaseState(database.get_db).wait_for_db()
        await app_instance.startup()
        await populate.populate_superuser()
        await populate.populate_from_csv()
        await app_instance.register_dynamic_endpoints()
        yield

    app_instance = App(settings, database, lifespan=lifespan)
    app_instance.get_app().add_middleware(AuthMiddleware, settings=settings)  # type: ignore

    return app_instance.get_app()


start_app = create_app()
