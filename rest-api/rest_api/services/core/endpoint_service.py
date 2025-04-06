from entities.core import Endpoint
from repositories.core import EndpointRepository
from schemas.core import EndpointCreate, EndpointResponse
from services.base import BaseService


class EndpointService(
    BaseService[Endpoint, EndpointRepository, EndpointCreate, EndpointResponse]
):
    _repository_cls = EndpointRepository
    _entity_cls = Endpoint
    _response_schema_cls = EndpointResponse
