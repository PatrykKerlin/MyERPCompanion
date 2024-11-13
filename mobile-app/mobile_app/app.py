import json
import os
import threading
import asyncio

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from controllers.core.login_controller import LoginController
from controllers.business.employee_controler import EmployeeController
from views.core.login_view import LoginView
from views.business.employee.all_employees_view import AllEmployeesView
from models.core.token_model import TokenModel


class App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.employee_controller = None
        self.login_controller = None
        self.screen_manager = None
        self.all_employees_view = None
        self.token_model = None
        self.login_view = None

        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file, 'r') as config_file:
            self.app_config = json.load(config_file)

    def build(self):
        self.theme_cls.theme_style = self.app_config.get('DEFAULT_THEME', 'Dark').capitalize()

        self.token_model = TokenModel()
        self.login_view = LoginView()
        self.all_employees_view = AllEmployeesView()

        self.login_controller = LoginController(self, self.login_view, self.app_config)
        self.employee_controller = EmployeeController(self.all_employees_view, self.app_config)

        self.login_view.controller = self.login_controller

        asyncio.run(self.login_controller.fetch_labels())

        self.screen_manager = ScreenManager()

        self.screen_manager.add_widget(self.login_view)
        self.screen_manager.add_widget(self.all_employees_view)

        return self.screen_manager

    def switch_to_all_employees(self):
        self.screen_manager.current = 'all_employees'
        asyncio.run(self.employee_controller.fetch_labels(self.token_model.token))
        asyncio.run(self.employee_controller.fetch_data(self.token_model.token))


if __name__ == '__main__':
    App().run()
