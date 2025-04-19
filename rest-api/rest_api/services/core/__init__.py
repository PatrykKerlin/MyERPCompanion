from utils.factories import ServiceFactory
from entities.core import Endpoint
from schemas.core import EndpointCreate, EndpointResponse
from repositories.core import EndpointRepository

from .group_service import GroupService
from .module_service import ModuleService
from .user_service import UserService

EndpointService = ServiceFactory.create(
    entity_cls=Endpoint,
    repository_cls=EndpointRepository,
    create_schema_cls=EndpointCreate,
    response_schema_cls=EndpointResponse,
)
