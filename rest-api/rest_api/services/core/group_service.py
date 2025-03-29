from dtos.core import GroupDTO
from entities.core import Group
from repositories.core import GroupRepository
from services.base import BaseService


class GroupService(BaseService):
    _dto = GroupDTO
    _entity = Group
    _repository = GroupRepository
