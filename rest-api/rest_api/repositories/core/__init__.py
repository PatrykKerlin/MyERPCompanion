from entities.core import *
from utils.factories import RepositoryFactory

from .group_repository import GroupRepository
from .module_repository import ModuleRepository
from .user_repository import UserRepository

EndpointRepository = RepositoryFactory.create(Endpoint)
