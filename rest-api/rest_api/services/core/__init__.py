from models.core import Endpoint, Group
from repositories.core import EndpointRepository, GroupRepository
from schemas.core import EndpointInputSchema, EndpointOutputSchema, GroupInputSchema, GroupOutputSchema
from utils.factories import ServiceFactory

from .module_service import ModuleService
from .text_service import TextService
from .user_service import UserService

EndpointService = ServiceFactory.create(
    model_cls=Endpoint,
    repository_cls=EndpointRepository,
    input_schema_cls=EndpointInputSchema,
    output_schema_cls=EndpointOutputSchema,
)
GroupService = ServiceFactory.create(
    model_cls=Group,
    repository_cls=GroupRepository,
    input_schema_cls=GroupInputSchema,
    output_schema_cls=GroupOutputSchema,
)


__all__ = [
    "EndpointService",
    "GroupService",
    "ModuleService",
    "TextService",
    "UserService",
]
