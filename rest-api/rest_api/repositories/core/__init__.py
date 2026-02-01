from models.core.assoc_module_group import AssocModuleGroup
from models.core.assoc_user_group import AssocUserGroup
from models.core.assoc_view_controller import AssocViewController
from models.core.controller import Controller
from models.core.group import Group
from models.core.image import Image
from models.core.language import Language
from models.core.view import View
from repositories.core.module_repository import ModuleRepository
from repositories.core.view_repository import ViewRepository
from repositories.core.translation_repository import TranslationRepository
from repositories.core.user_repository import UserRepository
from utils.repository_factory import RepositoryFactory

AssocModuleGroupRepository = RepositoryFactory.create(AssocModuleGroup)
AssocUserGroupRepository = RepositoryFactory.create(AssocUserGroup)
AssocViewControllerRepository = RepositoryFactory.create(AssocViewController)
ControllerRepository = RepositoryFactory.create(Controller)
GroupRepository = RepositoryFactory.create(Group)
ImageRepository = RepositoryFactory.create(Image)
LanguageRepository = RepositoryFactory.create(Language)
ViewRepository = ViewRepository

__all__ = [
    "AssocModuleGroupRepository",
    "AssocUserGroupRepository",
    "AssocViewControllerRepository",
    "ControllerRepository",
    "GroupRepository",
    "ImageRepository",
    "LanguageRepository",
    "ModuleRepository",
    "TranslationRepository",
    "UserRepository",
    "ViewRepository",
]
