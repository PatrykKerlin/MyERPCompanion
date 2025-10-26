from typing import Union, cast
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from models.core.image import Image
from repositories.core import ImageRepository
from schemas.core.image_schema import ImageStrictCreateSchema, ImageStrictUpdateSchema, ImagePlainSchema
from services.base.base_service import BaseService
from utils.file_storage import FileStorage


class ImageService(
    BaseService[Image, ImageRepository, Union[ImageStrictCreateSchema, ImageStrictUpdateSchema], ImagePlainSchema]
):
    _repository_cls = ImageRepository
    _model_cls = Image
    _output_schema_cls = ImagePlainSchema

    def __init__(self) -> None:
        super().__init__()
        allowed_content: dict[str, str] = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/avif": "avif",
        }
        self.__storage = FileStorage("/rest_api/media", "http://localhost:8000/media", allowed_content)

    async def create(
        self, session: AsyncSession, created_by: int, schema: Union[ImageStrictCreateSchema, ImageStrictUpdateSchema]
    ) -> ImagePlainSchema:
        public_url: str | None = None
        try:
            schema = cast(ImageStrictCreateSchema, schema)
            public_url = await self.__storage.save_file(
                item_id=schema.item_id,
                content_type=schema.content_type,
                data=schema.data,
            )
            schema = schema.model_copy(update={"url": public_url})
            return await super().create(session, created_by, schema)
        except:
            if public_url:
                await self.__storage.delete_file(public_url)
            raise

    async def delete(self, session: AsyncSession, model_id: int, modified_by: int) -> None:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        setattr(model, "modified_by", modified_by)
        url = model.url
        await self._repository_cls.delete(session, model)
        await self.__storage.delete_file(url)
