from models.core import AssocModuleGroup, AssocUserGroup, Group, Language, Theme, View, Image
from utils.factories import RepositoryFactory

from .module_repository import ModuleRepository
from .translation_repository import TranslationRepository
from .user_repository import UserRepository

AssocModuleGroupRepository = RepositoryFactory.create(AssocModuleGroup)
AssocUserGroupRepository = RepositoryFactory.create(AssocUserGroup)
GroupRepository = RepositoryFactory.create(Group)
ImageRepository = RepositoryFactory.create(Image)
LanguageRepository = RepositoryFactory.create(Language)
ThemeRepository = RepositoryFactory.create(Theme)
ViewRepository = RepositoryFactory.create(View)

__all__ = [
    "AssocModuleGroupRepository",
    "AssocUserGroupRepository",
    "GroupRepository",
    "ImageRepository",
    "LanguageRepository",
    "ModuleRepository",
    "ThemeRepository",
    "TranslationRepository",
    "UserRepository",
    "ViewRepository",
]
