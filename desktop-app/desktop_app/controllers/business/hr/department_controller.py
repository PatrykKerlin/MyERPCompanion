from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from services.business.hr import DepartmentService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.hr.department_view import DepartmentView


class DepartmentController(
    BaseViewController[DepartmentService, DepartmentView, DepartmentPlainSchema, DepartmentStrictSchema]
):
    _plain_schema_cls = DepartmentPlainSchema
    _strict_schema_cls = DepartmentStrictSchema
    _service_cls = DepartmentService
    _view_cls = DepartmentView
    _endpoint = Endpoint.DEPARTMENTS
    _view_key = View.DEPARTMENTS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> DepartmentView:
        return DepartmentView(self, translation, mode, event.view_key, event.data)
