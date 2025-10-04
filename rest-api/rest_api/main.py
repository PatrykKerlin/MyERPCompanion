from contextlib import asynccontextmanager
import importlib
from typing import Any, AsyncGenerator

from fastapi import APIRouter, FastAPI

from config import Context, CustomFastAPI, Database, Settings
from controllers import core as cc
from handlers import CheckDatabaseState, PopulateDatabase
from middlewares import AuthMiddleware, ViewMiddleware
from utils.auth import Auth


class App:
    def __init__(self, context: Context, database: Database, auth: Auth, lifespan: Any = None) -> None:
        self.__context = context
        self.__database = database
        self.__auth = auth
        self.__app = CustomFastAPI(
            title="MyERPCompanion API",
            redoc_url=None,
            lifespan=lifespan,
        )
        self.__include_routers()

    def __include_routers(self) -> None:
        api_router = APIRouter(prefix="/api")
        endpoints: list[dict[str, Any]] = []

        core_endpoints = [
            {"router": cc.HealthCheckController().router},
            {"router": cc.CurrentUserController(self.__context, self.__auth).router},
            {"router": cc.AuthController(self.__context.get_session, self.__auth).router, "prefix": "/auth"},
            {"router": cc.TranslationController(self.__context, self.__auth).router, "prefix": "/translations"},
            {"router": cc.ModuleController(self.__context, self.__auth).router, "prefix": "/modules"},
            {"router": cc.ViewController(self.__context, self.__auth).router, "prefix": "/views"},
            {"router": cc.UserController(self.__context, self.__auth).router, "prefix": "/users"},
            {"router": cc.GroupController(self.__context, self.__auth).router, "prefix": "/groups"},
            {"router": cc.LanguageController(self.__context, self.__auth).router, "prefix": "/languages"},
            {"router": cc.ThemeController(self.__context, self.__auth).router, "prefix": "/themes"},
        ]

        endpoints.extend(core_endpoints)

        for endpoint in endpoints:
            api_router.include_router(**endpoint)

        self.__app.include_router(api_router)

    async def startup(self) -> None:
        async with self.__database.engine.begin() as conn:
            await conn.run_sync(Database.get_base().metadata.create_all)

    def get_app(self) -> FastAPI:
        return self.__app


def create_app() -> FastAPI:
    settings = Settings()  # type: ignore
    database = Database(settings)
    context = Context(settings=settings, get_session=database.get_session)
    auth = Auth(context)

    def load_all_models() -> None:
        for models in ("models.base", "models.business", "models.core"):
            importlib.import_module(models)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        load_all_models()
        populate_database = PopulateDatabase(database.get_session, auth)
        await CheckDatabaseState(database.get_session).wait_for_db()
        await app_instance.startup()
        await populate_database.execute()
        yield

    app_instance = App(context=context, database=database, auth=auth, lifespan=lifespan)
    app_instance.get_app().add_middleware(AuthMiddleware, get_session=context.get_session, auth=auth)  # type: ignore
    app_instance.get_app().add_middleware(ViewMiddleware, context=context)  # type: ignore

    return app_instance.get_app()


start_app = create_app()
