from entities.core import *
from schemas.core import *
from services.core import *
from utils.factories import ControllerFactory

from .auth_controller import AuthController
from .health_check_controller import HealthCheckController
from .user_controller import UserController

EndpointController = ControllerFactory.create(
    entity_cls=Endpoint,
    service_cls=EndpointService,
    create_schema_cls=EndpointCreate,
    response_schema_cls=EndpointResponse,
)

GroupController = ControllerFactory.create(
    entity_cls=Group,
    service_cls=GroupService,
    create_schema_cls=GroupCreate,
    response_schema_cls=GroupResponse,
)
