import base64
from typing import Union

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import HTTPException, Request, status
from schemas.core.image_schema import (
    ImagePlainSchema,
    ImageStrictCreateSchema,
    ImageStrictUpdateSchema,
)
from services.core import ImageService
from starlette.datastructures import UploadFile as StarletteUploadFile
from utils.auth import Auth
from utils.enums import Action


class ImageController(
    BaseController[ImageService, Union[ImageStrictCreateSchema, ImageStrictUpdateSchema], ImagePlainSchema]
):
    _input_schema_cls = ImageStrictCreateSchema
    _service_cls = ImageService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        include = {
            Action.GET_ALL: True,
            Action.GET_ONE: True,
            Action.CREATE: True,
            Action.UPDATE: True,
            Action.UPDATE_BULK: True,
            Action.DELETE: True,
        }
        self._service.set_storage(self._settings.MEDIA_DIR, self._settings.MEDIA_URL)
        self._register_routes(ImagePlainSchema, include=include)

    @BaseController.handle_exceptions()
    async def create(self, request: Request) -> ImagePlainSchema:
        user = request.state.user
        schema = await self.__parse_create_payload(request)
        session = BaseController._get_request_session(request)
        return await self._service.create(session, user.id, schema)

    @BaseController.handle_exceptions()
    async def update(self, request: Request, model_id: int) -> ImagePlainSchema:
        user = request.state.user
        body = await request.json()
        schema = ImageStrictUpdateSchema(**body)
        session = BaseController._get_request_session(request)
        return await self._service.update(session, model_id, user.id, schema)

    @BaseController.handle_exceptions(bulk=True)
    async def update_bulk(self, request: Request) -> list[ImagePlainSchema]:
        user = request.state.user
        body = await request.json()
        if not isinstance(body, list):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        items: list[tuple[int, ImageStrictUpdateSchema]] = []
        for item in body:
            if not isinstance(item, dict):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            model_id = item.get("id")
            if not isinstance(model_id, int):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            data = {key: value for key, value in item.items() if key != "id"}
            schema = ImageStrictUpdateSchema(**data)
            items.append((model_id, schema))
        session = BaseController._get_request_session(request)
        return await self._service.update_bulk(session=session, items=items, modified_by=user.id)

    async def __parse_create_payload(self, request: Request) -> ImageStrictCreateSchema:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            body = await request.json()
            data_value = body.get("data")
            try:
                body["data"] = base64.b64decode(data_value)
            except Exception:
                self._logger.exception(f"InvalidBase64Payload in {self.__class__.__name__}.__parse_create_payload")
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
