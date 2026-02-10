from collections.abc import Mapping
from types import new_class
from typing import Any, TypeVar

from config.context import Context
from controllers.base.base_controller import BaseController
from models.base.base_model import BaseModel
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.auth import Auth
from utils.enums import Action

TModel = TypeVar("TModel", bound=BaseModel)
TInputSchema = TypeVar("TInputSchema", bound=BaseStrictSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BasePlainSchema)
TService = TypeVar("TService", bound=BaseService)


class ControllerFactory:
    @classmethod
    def create(
        cls,
        model_cls: type[TModel],
        service_cls: type[TService],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
        path: str = "",
        include: Mapping[Action, bool] | None = None,
    ) -> type[BaseController[TService, TInputSchema, TOutputSchema]]:

        def exec_body(namespace: dict[str, Any]) -> None:
            def __init__(self, context: Context, auth: Auth) -> None:
                BaseController.__init__(self, context, auth)
                self._register_routes(
                    output_schema=output_schema_cls,
                    include=include,
                    path=path,
                )

            namespace["_input_schema_cls"] = input_schema_cls
            namespace["_service_cls"] = service_cls
            namespace["__init__"] = __init__

        actions_mapping = {
            Action.GET_ALL: True,
            Action.GET_ONE: True,
            Action.CREATE: True,
            Action.UPDATE: True,
            Action.DELETE: True,
        }

        include = include or actions_mapping

        return new_class(
            f"{model_cls.__name__}Controller",
            [BaseController[service_cls, input_schema_cls, output_schema_cls]],
            exec_body=exec_body,
        )
