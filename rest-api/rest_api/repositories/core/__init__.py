from models.core.assoc_module_group import AssocModuleGroup
from models.core.assoc_user_group import AssocUserGroup
from models.core.group import Group
from models.core.image import Image
from models.core.language import Language
from models.core.theme import Theme
from models.core.view import View
from repositories.core.module_repository import ModuleRepository
from repositories.core.translation_repository import TranslationRepository
from repositories.core.user_repository import UserRepository
from utils.repository_factory import RepositoryFactory

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
