from controllers.base import BaseController
from services.core import AppService
from views.core import AppWindow


class AppController(BaseController):
    _service_cls = AppService
    _view_cls = AppWindow

    def show(self):
        super().show()
        self._context.controllers.auth.show()
