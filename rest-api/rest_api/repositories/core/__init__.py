from models.core import AssocModuleGroup, AssocUserGroup, Group, Image, Language, Theme, View
from utils.factories import RepositoryFactory

from .module_repository import ModuleRepository
from .translation_repository import TranslationRepository
from .user_repository import UserRepository
from .view_repository import ViewRepository

AssocModuleGroupRepository = RepositoryFactory.create(AssocModuleGroup)
AssocUserGroupRepository = RepositoryFactory.create(AssocUserGroup)
GroupRepository = RepositoryFactory.create(Group)
ImageRepository = RepositoryFactory.create(Image)
LanguageRepository = RepositoryFactory.create(Language)
ThemeRepository = RepositoryFactory.create(Theme)

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
