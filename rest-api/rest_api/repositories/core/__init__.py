from models.core import AssocGroupModule, AssocUserGroup, View, Group, Language, Theme
from utils.factories import RepositoryFactory

from .module_repository import ModuleRepository
from .translation_repository import TranslationRepository
from .user_repository import UserRepository

AssocGroupModuleRepository = RepositoryFactory.create(AssocGroupModule)
AssocUserGroupRepository = RepositoryFactory.create(AssocUserGroup)
GroupRepository = RepositoryFactory.create(Group)
LanguageRepository = RepositoryFactory.create(Language)
ThemeRepository = RepositoryFactory.create(Theme)
ViewRepository = RepositoryFactory.create(View)

__all__ = [
    "AssocGroupModuleRepository",
    "AssocUserGroupRepository",
    "GroupRepository",
    "LanguageRepository",
    "ModuleRepository",
    "ThemeRepository",
    "TranslationRepository",
    "UserRepository",
    "ViewRepository",
]
