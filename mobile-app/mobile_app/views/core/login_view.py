from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel


class LoginView(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        self.__login_input = MDTextField()
        self.add_widget(self.__login_input)
        self.__password_input = MDTextField(password=True)
        self.add_widget(self.__password_input)

        self.__sign_in_button = MDRaisedButton()
        self.__sign_in_button.bind()
        self.add_widget(self.__sign_in_button)

        self.__error_label = MDLabel()
        self.add_widget(self.__error_label)

    def set_labels(self, labels):
        self.__login_input.text = labels.get('login', {}).get('value', '')
        self.__password_input.text = labels.get('password', {}).get('value', '')

    def on_sign_in_button_press(self, instance):
        login = self.__login_input.text
        password = self.__password_input.text
        self.controller.login(login, password)

    def display_error(self, message):
        self.__error_label.text = message
