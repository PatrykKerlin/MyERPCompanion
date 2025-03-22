from fastapi import APIRouter


class HealthCheckController:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/health-check", self.health_check, methods=["GET"])

    @staticmethod
    async def health_check() -> dict:
        return {"status": "OK"}
