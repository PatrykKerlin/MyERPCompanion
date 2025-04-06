from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class CustomFastAPI(FastAPI):
    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(title=title, **kwargs)
        self.openapi_schema = None

    def openapi(self) -> dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title=self.title,
            version="1.0.0",
            description="MyERPCompanion API documentation",
            routes=self.routes,
        )
        openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {"type": "http", "scheme": "bearer"}
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        self.openapi_schema = openapi_schema
        return self.openapi_schema
