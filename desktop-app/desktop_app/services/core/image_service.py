from typing import Any, Union

from schemas.core.image_schema import (
    ImageMultipartPayloadSchema,
    ImagePlainSchema,
    ImageStrictCreateSchema,
    ImageStrictUpdateSchema,
)
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class ImageService(
    BaseService[ImagePlainSchema, Union[ImageStrictCreateSchema, ImageStrictUpdateSchema, ImageMultipartPayloadSchema]]
):
    _plain_schema_cls = ImagePlainSchema

    @BaseService.handle_token_refresh
    async def create(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: (
            Union[
                ImageStrictCreateSchema,
                ImageStrictUpdateSchema,
                ImageMultipartPayloadSchema,
                list[ImageStrictCreateSchema | ImageStrictUpdateSchema],
                IdsPayloadSchema,
            ]
            | None
        ) = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> ImagePlainSchema:
        if isinstance(body_params, ImageStrictCreateSchema):
            resolved_body_params = body_params.model_dump()
        else:
            resolved_body_params = {}
        response = await self._post(
            endpoint=endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    @BaseService.handle_token_refresh
    async def update(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: (
            Union[
                ImageStrictCreateSchema,
                ImageStrictUpdateSchema,
                ImageMultipartPayloadSchema,
                list[ImageStrictCreateSchema | ImageStrictUpdateSchema],
                IdsPayloadSchema,
            ]
            | None
        ) = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> ImagePlainSchema:
        if isinstance(body_params, ImageStrictUpdateSchema):
            resolved_body_params = body_params.model_dump()
        else:
            resolved_body_params = {}
        resolved_endpoint = f"{endpoint}/{path_param}"
        response = await self._put(
            endpoint=resolved_endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)
