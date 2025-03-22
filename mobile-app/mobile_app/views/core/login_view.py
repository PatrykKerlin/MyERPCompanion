from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import mainthread
import asyncio


class LoginView(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        self.controller = None

        box_layout = BoxLayout(orientation='vertical', spacing=20, padding=[50, 100, 50, 100])

        self.__login_input = MDTextField()
        box_layout.add_widget(self.__login_input)

        self.__password_input = MDTextField(password=True)
        box_layout.add_widget(self.__password_input)

        self.__sign_in_button = MDRaisedButton(pos_hint={'center_x': 0.5})
        self.__sign_in_button.bind(on_release=self.on_sign_in_button_press)
        box_layout.add_widget(self.__sign_in_button)

        self.__error_label = MDLabel(theme_text_color='Error', halign='center')
        box_layout.add_widget(self.__error_label)

        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor_layout.add_widget(box_layout)

        self.add_widget(anchor_layout)

    @mainthread
    def set_labels(self, labels):
        self.__login_input.hint_text = labels.get('login', {}).get('value', 'Login')
        self.__password_input.hint_text = labels.get('password', {}).get('value', 'Password')
        self.__sign_in_button.text = labels.get('sign_in', {}).get('value', 'Sign In')

    def on_sign_in_button_press(self, instance):
        asyncio.run(self._handle_login())

    async def _handle_login(self):
        login = self.__login_input.text
        password = self.__password_input.text
        await self.controller.login(login, password)

    @mainthread
    def display_error(self, message):
        self.__error_label.text = message
