from dtos.core import EndpointDTO
from entities.core import Endpoint
from repositories.core import EndpointRepository
from services.base import BaseService


class EndpointService(BaseService):
    _dto = EndpointDTO
    _entity = Endpoint
    _repository = EndpointRepository
