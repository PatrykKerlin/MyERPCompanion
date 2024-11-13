import httpx
from httpx import AsyncClient, HTTPStatusError
from kivy.clock import mainthread


class LoginController:
    def __init__(self, app, view, config):
        self.__app = app
        self.__view = view
        self.__config = config
        self.__labels = None

    async def fetch_labels(self):
        url = self.__config['API_BASE_URL'] + '/view-content/' + self.__config['DEFAULT_LANGUAGE'] + '/login/'

        async with AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                labels = data.get('labels', {})
                self.__update_view_labels(labels)
                self.__labels = labels
            except HTTPStatusError as err:
                self.__view.display_error(f'Error: {err}')

    async def login(self, login, password):
        url = self.__config['API_BASE_URL'] + '/token/'
        payload = {'login': login, 'password': password}

        async with AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                token = response.json().get('token', None)
                self.__on_login_success(token)
            except HTTPStatusError:
                message = self.__labels.get('invalid_credentials', {}).get('value', 'Invalid credentials')
                self.__on_login_failure(message)

    @mainthread
    def __update_view_labels(self, labels):
        self.__view.set_labels(labels)

    @mainthread
    def __on_login_success(self, token):
        self.__app.token_model.token = token
        self.__app.switch_to_all_employees()

    @mainthread
    def __on_login_failure(self, message):
        self.__view.display_error(message)
