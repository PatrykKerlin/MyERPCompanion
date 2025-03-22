from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class CustomFastAPI(FastAPI):
    def __init__(self, title, **kwargs) -> None:
        super().__init__(**kwargs)
        self.openapi_schema = None
        self.title = title

    def openapi(self) -> dict:
        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title=self.title,
            version="1.0.0",
            description="MyERPCompanion API documentation",
            routes=self.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {"type": "http", "scheme": "bearer"}
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        self.openapi_schema = openapi_schema
        return self.openapi_schema
