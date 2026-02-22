from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from services.core import GroupService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.group_view import GroupView


class GroupController(BaseViewController[GroupService, GroupView, GroupPlainSchema, GroupStrictSchema]):
    _plain_schema_cls = GroupPlainSchema
    _strict_schema_cls = GroupStrictSchema
    _service_cls = GroupService
    _view_cls = GroupView
    _endpoint = Endpoint.GROUPS
    _view_key = View.GROUPS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> GroupView:
        return GroupView(self, translation, mode, event.view_key, event.data)
