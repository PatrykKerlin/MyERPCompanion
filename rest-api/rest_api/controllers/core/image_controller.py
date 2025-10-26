import base64
from typing import Union

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from controllers.base.base_controller import BaseController
from schemas.core.image_schema import ImagePlainSchema, ImageStrictCreateSchema, ImageStrictUpdateSchema
from services.core import ImageService
from config.context import Context
from utils.auth import Auth
from starlette.datastructures import UploadFile as StarletteUploadFile


class ImageController(
    BaseController[ImageService, Union[ImageStrictCreateSchema, ImageStrictUpdateSchema], ImagePlainSchema]
):
    _input_schema_cls = ImageStrictCreateSchema
    _service_cls = ImageService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._service.set_storage(self._settings.MEDIA_DIR, self._settings.MEDIA_URL)
        self._register_routes(ImagePlainSchema)

    async def create(self, request: Request) -> ImagePlainSchema:
        try:
            user = request.state.user
            schema = await self.__parse_create_payload(request)
            async with self._get_session() as session:
                return await self._service.create(session, user.id, schema)
        except HTTPException:
            raise
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def update(self, request: Request, model_id: int) -> ImagePlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            schema = ImageStrictUpdateSchema(**body)
            async with self._get_session() as session:
                return await self._service.update(session, model_id, user.id, schema)
        except HTTPException:
            raise
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def __parse_create_payload(self, request: Request) -> ImageStrictCreateSchema:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            body = await request.json()
            data_value = body.get("data")
            try:
                body["data"] = base64.b64decode(data_value)
            except Exception:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return ImageStrictCreateSchema(**body)
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            data_field = form.get("data")
            if not isinstance(data_field, StarletteUploadFile):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            file_bytes = await data_field.read()
            payload = {
                "url": form.get("url"),
                "is_primary": form.get("is_primary"),
                "order": form.get("order"),
                "description": form.get("description"),
                "content_type": form.get("content_type"),
                "data": file_bytes,
                "item_id": form.get("item_id"),
            }
            return ImageStrictCreateSchema(**payload)
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Media Type")
