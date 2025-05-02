from services.core import AuthService
from views.core import BaseView


class AppController:
    def __init__(self, service: AuthService, view: BaseView) -> None:
        self.service = service
        self.view = view

    def handle_login(self, username: str, password: str) -> None:
        try:
            token = self.service.login(username, password)
            self.view.update_message(f"Token: {token.access}")
        except Exception as e:
            self.view.update_message(str(e))
