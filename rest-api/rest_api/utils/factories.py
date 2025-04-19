from types import new_class
from typing import TYPE_CHECKING, Any

from config import Context

if TYPE_CHECKING:
    from ..controllers.base import BaseController
    from ..entities.base import BaseEntity
    from ..repositories.base import BaseRepository
    from ..schemas.base import BaseCreateSchema, BaseResponseSchema
    from ..services.base import BaseService


class RepositoryFactory:
    @classmethod
    def create(
        cls, entity_cls: type["BaseEntity"]
    ) -> type["BaseRepository[BaseEntity]"]:
        from repositories.base import BaseRepository

        return new_class(
            f"{entity_cls.__name__}Repository",
            [BaseRepository[entity_cls]],
            exec_body=lambda namespace: namespace.update({"_model_cls": entity_cls}),
        )


class ServiceFactory:
    @classmethod
    def create(
        cls,
        entity_cls: type["BaseEntity"],
        repository_cls: type["BaseRepository[BaseEntity]"],
        create_schema_cls: type["BaseCreateSchema"],
        response_schema_cls: type["BaseResponseSchema"],
    ) -> type[
        "BaseService[BaseEntity, BaseRepository[BaseEntity], BaseCreateSchema, BaseResponseSchema]"
    ]:
        from services.base import BaseService

        return new_class(
            f"{entity_cls.__name__}Service",
            [
                BaseService[
                    entity_cls, repository_cls, create_schema_cls, response_schema_cls
                ]
            ],
            exec_body=lambda namespace: namespace.update(
                {
                    "_repository_cls": repository_cls,
                    "_entity_cls": entity_cls,
                    "_response_schema_cls": response_schema_cls,
                }
            ),
        )


class ControllerFactory:
    @classmethod
    def create(
        cls,
        entity_cls: type["BaseEntity"],
        service_cls: type["BaseService"],
        create_schema_cls: type["BaseCreateSchema"],
        response_schema_cls: type["BaseResponseSchema"],
        path: str = "",
        include: list[str] | None = None,
    ) -> type["BaseController"]:
        from controllers.base import BaseController

        def exec_body(namespace: dict[str, Any]) -> None:
            def __init__(self, context: Context) -> None:
                BaseController.__init__(self, context)
                self._register_routes(
                    response_schema=response_schema_cls,
                    include=selected_methods,
                    path=path,
                )

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

        invalid = [
            method for method in selected_methods if method not in allowed_methods
        ]
        if invalid:
            raise ValueError(
                f"Invalid method(s): {invalid}. Allowed: {list(allowed_methods)}"
            )

        return new_class(
            f"{entity_cls.__name__}Controller",
            [BaseController[service_cls, create_schema_cls, response_schema_cls]],
            exec_body=exec_body,
        )
