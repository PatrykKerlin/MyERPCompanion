from sqlalchemy.ext.asyncio import AsyncSession

from models.core import View
from repositories.base import BaseRepository


class ViewRepository(BaseRepository[View]):
    _model_cls = View

    @classmethod
    async def get_one_by_key(cls, session: AsyncSession, key: str) -> View | None:
        query = super()._build_query([cls._expr(cls._model_cls.key == key)])
        result = await session.execute(query)
        return result.scalars().first()
