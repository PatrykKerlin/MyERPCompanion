from models.core import AssocGroupModule, AssocUserGroup, Endpoint, Group, Language, Theme
from utils.factories import RepositoryFactory

from .module_repository import ModuleRepository
from .text_repository import TextRepository
from .user_repository import UserRepository

AssocGroupModuleRepository = RepositoryFactory.create(AssocGroupModule)
AssocUserGroupRepository = RepositoryFactory.create(AssocUserGroup)
EndpointRepository = RepositoryFactory.create(Endpoint)
GroupRepository = RepositoryFactory.create(Group)
LanguageRepository = RepositoryFactory.create(Language)
ThemeRepository = RepositoryFactory.create(Theme)

__all__ = [
    "AssocGroupModuleRepository",
    "AssocUserGroupRepository",
    "EndpointRepository",
    "GroupRepository",
    "LanguageRepository",
    "ModuleRepository",
    "TextRepository",
    "ThemeRepository",
    "UserRepository",
]
