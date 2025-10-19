from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.hr.department_schema import DepartmentPlainSchema, DepartmentStrictSchema
from services.business.hr import DepartmentService
from utils.enums import Endpoint, View, ViewMode
from views.business.hr.department_view import DepartmentView
from events.events import ViewRequested, ViewReady


class DepartmentController(
    BaseViewController[DepartmentService, DepartmentView, DepartmentPlainSchema, DepartmentStrictSchema]
):
    _input_schema_cls = DepartmentPlainSchema
    _output_schema_cls = DepartmentStrictSchema
    _service_cls = DepartmentService
    _view_cls = DepartmentView
    _endpoint = Endpoint.DEPARTMENTS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key != View.DEPARTMENTS:
            return
        self._open_loading_dialog()
        translation_service = self._state_store.app_state.translation
        self._key = event.key
        if event.data:
            mode = ViewMode.READ
            self._request_data.input_values = event.data
        else:
            mode = ViewMode.SEARCH
        self._view = DepartmentView(self, translation_service.items, mode, event.key, event.data)
        await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()
