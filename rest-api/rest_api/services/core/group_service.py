from entities.core import Group
from repositories.core import GroupRepository
from schemas.core import GroupCreate, GroupResponse
from services.base import BaseService


class GroupService(BaseService[Group, GroupRepository, GroupCreate, GroupResponse]):
    _repository_cls = GroupRepository
    _entity_cls = Group
    _response_schema_cls = GroupResponse
