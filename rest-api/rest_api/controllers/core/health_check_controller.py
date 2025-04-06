from fastapi import APIRouter
from fastapi.responses import JSONResponse


class HealthCheckController:
    router = APIRouter()

    @staticmethod
    @router.get(path="/health-check")
    async def health_check() -> JSONResponse:
        return JSONResponse({"status": "OK"})
