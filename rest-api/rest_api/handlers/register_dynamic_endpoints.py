import importlib
from fastapi import APIRouter
from sqlalchemy import select

from models.core import Module


class RegisterDynamicModules:
    def __init__(self, context, app) -> None:
        self._context = context
        self._app = app
        self._api_router = APIRouter(prefix="/api")

    @staticmethod
    def _import_controller(controller_name: str):
        module = importlib.import_module("controllers.core")
        return getattr(module, controller_name)

    async def register(self) -> None:
        async with self._context.get_db() as db:
            result = await db.execute(select(Module).where(Module.is_enabled == True))
            modules = result.scalars().all()

            for mod in modules:
                try:
                    ControllerClass = self._import_controller(mod.controller_name)
                    controller = ControllerClass(self._context)
                    controller.module_name = mod.name  # jeśli dziedziczy po SecuredController
                    self._api_router.include_router(
                        controller.router,
                        prefix=mod.path,
                        tags=[mod.name],
                    )
                except Exception as e:
                    print(f"[!] Failed to load controller {mod.controller_name}: {e}")

        self._app.include_router(self._api_router)
