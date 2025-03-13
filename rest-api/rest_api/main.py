from fastapi import FastAPI, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from config import Settings
from config import Database
from controllers import core
from handlers import DBCheck, PopulateDB


class App:
    def __init__(self, settings: Settings, database: Database, oauth2_scheme: OAuth2PasswordBearer) -> None:
        self.__settings = settings
        self.__database = database
        self.__oauth2_scheme = oauth2_scheme
        self.__app = FastAPI(
            title="MyERPCompanion API",
            # docs_url=None,
            redoc_url=None,
            # openapi_url=None
        )
        self.__include_routers()

    def __include_routers(self) -> None:
        api_router = APIRouter(prefix="/api")

        health_check_controller = core.HealthCheckController()
        login_controller = core.AuthController(self.__database.get_db, self.__settings)
        current_user_controller = core.CurrentUserController(self.__database.get_db, self.__settings,
                                                             self.__oauth2_scheme)
        user_controller = core.UserController(self.__database.get_db, self.__settings, self.__oauth2_scheme)
        group_controller = core.GroupController(self.__database.get_db)

        api_router.include_router(health_check_controller.router, tags=["Health Check"])
        api_router.include_router(login_controller.router, tags=["Authorization"])
        api_router.include_router(current_user_controller.router, tags=["Current User"])
        api_router.include_router(user_controller.router, prefix="/users", tags=["Users"])
        api_router.include_router(group_controller.router, prefix="/groups", tags=["Groups"])

        self.__app.include_router(api_router)

    async def startup(self) -> None:
        async with self.__database.engine.begin() as conn:
            await conn.run_sync(Database.get_base().metadata.create_all)

    def get_app(self) -> FastAPI:
        return self.__app


def create_app() -> FastAPI:
    settings = Settings()
    database = Database(settings)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")
    app_instance = App(settings, database, oauth2_scheme)
    app = app_instance.get_app()

    @app.on_event("startup")
    async def on_startup():
        db_check = DBCheck(database.get_db)
        populate_db = PopulateDB(database.get_db)

        await db_check.wait_for_db()
        await populate_db.populate_db()
        await app_instance.startup()

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version="1.0.0",
            description="MyERPCompanion API documentation",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            }
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


app = create_app()
