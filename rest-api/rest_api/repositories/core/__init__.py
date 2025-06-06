from models.core import Endpoint, Group, SettingKey, Text
from utils.factories import RepositoryFactory

from .module_repository import ModuleRepository
from .setting_repository import SettingRepository
from .text_repository import TextRepository
from .user_repository import UserRepository

EndpointRepository = RepositoryFactory.create(Endpoint)
GroupRepository = RepositoryFactory.create(Group)
SettingKeyRepository = RepositoryFactory.create(SettingKey)

__all__ = [
    "EndpointRepository",
    "GroupRepository",
    "ModuleRepository",
    "SettingKeyRepository",
    "SettingRepository",
    "TextRepository",
    "UserRepository",
]
