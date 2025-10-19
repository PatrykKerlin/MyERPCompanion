import importlib
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import APIRouter, FastAPI

from config.context import Context
from config.database import Database
from config.settings import Settings
from controllers import core
from controllers.business import hr, logistic, trade
from handlers.check_database_state import CheckDatabaseState
from handlers.populate_database import PopulateDatabase
from middlewares.auth_middleware import AuthMiddleware
from middlewares.view_middleware import ViewMiddleware
from utils.auth import Auth


class App:
    def __init__(self, context: Context, database: Database, auth: Auth, lifespan: Any = None) -> None:
        self.__context = context
        self.__database = database
        self.__auth = auth
        self.__app = FastAPI(
            title="MyERPCompanion API",
            redoc_url=None,
            lifespan=lifespan,
        )
        self.__include_routers()

    def __include_routers(self) -> None:
        api_router = APIRouter(prefix="/api")
        endpoints: list[dict[str, Any]] = []

        core_endpoints = [
            {"router": core.HealthCheckController().router},
            {"router": core.CurrentUserController(self.__context, self.__auth).router},
            {"router": core.AuthController(self.__context.get_session, self.__auth).router, "prefix": "/auth"},
            {"router": core.TranslationController(self.__context, self.__auth).router, "prefix": "/translations"},
            {"router": core.ModuleController(self.__context, self.__auth).router, "prefix": "/modules"},
            {"router": core.ViewController(self.__context, self.__auth).router, "prefix": "/views"},
            {"router": core.UserController(self.__context, self.__auth).router, "prefix": "/users"},
            {"router": core.GroupController(self.__context, self.__auth).router, "prefix": "/groups"},
            {"router": core.LanguageController(self.__context, self.__auth).router, "prefix": "/languages"},
            {"router": core.ThemeController(self.__context, self.__auth).router, "prefix": "/themes"},
        ]
        business_hr_endpoints = [
            {"router": hr.DepartmentController(self.__context, self.__auth).router, "prefix": "/departments"},
            {"router": hr.EmployeeController(self.__context, self.__auth).router, "prefix": "/employees"},
            {"router": hr.PositionController(self.__context, self.__auth).router, "prefix": "/positions"},
        ]
        business_logistic_endpoints = [
            {"router": logistic.BinController(self.__context, self.__auth).router, "prefix": "/bins"},
            {"router": logistic.WarehouseController(self.__context, self.__auth).router, "prefix": "/warehouses"},
        ]
        business_trade_endpoints = [
            {"router": trade.CurrencyController(self.__context, self.__auth).router, "prefix": "/currencies"},
        ]

        endpoints.extend(core_endpoints)
        endpoints.extend(business_hr_endpoints)
        endpoints.extend(business_logistic_endpoints)
        endpoints.extend(business_trade_endpoints)

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
        for models in ("models.business.hr", "models.business.logistic", "models.business.trade", "models.core"):
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
