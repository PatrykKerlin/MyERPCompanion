from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class EngineProvider:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def create(self) -> AsyncEngine:
        return create_async_engine(self._database_url, pool_pre_ping=True)
