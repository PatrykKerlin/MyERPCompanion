from typing import Union, cast

from models.core.image import Image
from repositories.core import ImageRepository
from schemas.core.image_schema import (
    ImageModelSchema,
    ImagePlainSchema,
    ImageStrictCreateSchema,
    ImageStrictUpdateSchema,
)
from services.base.base_service import BaseService
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from utils.file_storage import FileStorage


class ImageService(
    BaseService[
        Image,
        ImageRepository,
        Union[ImageModelSchema, ImageStrictCreateSchema, ImageStrictUpdateSchema],
        ImagePlainSchema,
    ]
):
    _repository_cls = ImageRepository
    _model_cls = Image
    _output_schema_cls = ImagePlainSchema

    def __init__(self) -> None:
        super().__init__()
        self.__allowed_content: dict[str, str] = {
            "image/jpeg": "jpg",
            "image/png": "png",
        }
        self.__storage: FileStorage | None = None

    def set_storage(self, media_dir: str, media_url: str) -> None:
        self.__storage = FileStorage(
            root_dir=f"{media_dir}/images", base_url=f"{media_url}/images", allowed_content=self.__allowed_content
        )

    async def create(
        self,
        session: AsyncSession,
        created_by: int,
        schema: Union[ImageModelSchema, ImageStrictCreateSchema, ImageStrictUpdateSchema],
    ) -> ImagePlainSchema:
        if not self.__storage:
            raise RuntimeError("File storage service is not initialized")
        public_url: str | None = None
        try:
            schema = cast(ImageStrictCreateSchema, schema)
            public_url = await self.__storage.save_file(
                item_id=schema.item_id,
                content_type=schema.content_type,
                data=schema.data,
            )
            model_schema = ImageModelSchema(
                url=public_url,
                is_primary=schema.is_primary,
                order=schema.order,
                description=schema.description,
                item_id=schema.item_id,
            )
            model = self._model_cls(**model_schema.model_dump())
            model.created_by = created_by
            saved_model = await self._repository_cls.save(session, model)
            loaded_model = await self._repository_cls.get_one_by_id(session, saved_model.id)
            if not loaded_model:
                raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=saved_model.id))
            return self._output_schema_cls.model_validate(loaded_model)
        except:
            if public_url:
                await self.__storage.delete_file(public_url)
            raise

    async def delete(self, session: AsyncSession, model_id: int, modified_by: int) -> None:
        if not self.__storage:
            return
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        setattr(model, "is_primary", False)
        setattr(model, "modified_by", modified_by)
        url = model.url
        await self._repository_cls.delete(session, model)
        await self.__storage.delete_file(url)
