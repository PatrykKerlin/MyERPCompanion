from types import new_class
from typing import TYPE_CHECKING, Any, TypeVar

from config import Context

if TYPE_CHECKING:
    from ..controllers.base import BaseController
    from ..models.base import BaseModel
    from ..repositories.base import BaseRepository
    from ..schemas.base import BasePlainSchema, BaseStrictSchema
    from ..services.base import BaseService


TModel = TypeVar("TModel", bound="BaseModel")
TInputSchema = TypeVar("TInputSchema", bound="BaseStrictSchema")
TOutputSchema = TypeVar("TOutputSchema", bound="BasePlainSchema")
TRepository = TypeVar("TRepository", bound="BaseRepository")
TService = TypeVar("TService", bound="BaseService")
TController = TypeVar("TController", bound="BaseController")


class RepositoryFactory:
    @classmethod
    def create(cls, model_cls: type[TModel]) -> type["BaseRepository[TModel]"]:
        from repositories.base import BaseRepository

        return new_class(
            f"{model_cls.__name__}Repository",
            [BaseRepository[model_cls]],
            exec_body=lambda namespace: namespace.update({"_model_cls": model_cls}),
        )


class ServiceFactory:
    @classmethod
    def create(
        cls,
        model_cls: type[TModel],
        repository_cls: type[TRepository],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
    ) -> type["BaseService[TModel, TRepository, TInputSchema, TOutputSchema]"]:
        from services.base import BaseService

        return new_class(
            f"{model_cls.__name__}Service",
            [BaseService[model_cls, repository_cls, input_schema_cls, output_schema_cls]],
            exec_body=lambda namespace: namespace.update(
                {
                    "_repository_cls": repository_cls,
                    "_model_cls": model_cls,
                    "_output_schema_cls": output_schema_cls,
                }
            ),
        )


class ControllerFactory:
    @classmethod
    def create(
        cls,
        model_cls: type[TModel],
        service_cls: type[TService],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
        path: str = "",
        include: list[str] | None = None,
    ) -> type["BaseController[TService, TInputSchema, TOutputSchema]"]:
        from controllers.base import BaseController

        def exec_body(namespace: dict[str, Any]) -> None:
            def __init__(self, context: Context) -> None:
                BaseController.__init__(self, context)
                self._register_routes(
                    output_schema=output_schema_cls,
                    include=selected_methods,
                    path=path,
                )

            namespace["_input_schema_cls"] = input_schema_cls
            namespace["_service_cls"] = service_cls
            namespace["__init__"] = __init__

        method_map = {
            "get_all": BaseController.get_all,
            "get_by_id": BaseController.get_by_id,
            "create": BaseController.create,
            "update": BaseController.update,
            "delete": BaseController.delete,
        }

        allowed_methods = method_map.keys()
        selected_methods = include or list(allowed_methods)

        invalid = [method for method in selected_methods if method not in allowed_methods]
        if invalid:
            raise ValueError(f"Invalid method(s): {invalid}. Allowed: {list(allowed_methods)}")

        return new_class(
            f"{model_cls.__name__}Controller",
            [BaseController[service_cls, input_schema_cls, output_schema_cls]],
            exec_body=exec_body,
        )
