from entities.core import Endpoint
from repositories.base import BaseRepository


class EndpointRepository(BaseRepository[Endpoint]):
    _model_cls = Endpoint
