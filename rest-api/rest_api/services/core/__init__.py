from entities.core import *
from repositories.core import *
from schemas.core import *
from utils.factories import ServiceFactory

from .group_service import GroupService
from .module_service import ModuleService
from .user_service import UserService

EndpointService = ServiceFactory.create(
    entity_cls=Endpoint,
    repository_cls=EndpointRepository,
    create_schema_cls=EndpointCreate,
    response_schema_cls=EndpointResponse,
)
