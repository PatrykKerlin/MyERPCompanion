from httpx import AsyncClient, HTTPStatusError
from kivy.clock import mainthread


class LoginController:
    def __init__(self, app, view, config):
        self.__app = app
        self.__view = view
        self.__config = config
        self.__labels = self.__fetch_labels()

    async def __fetch_labels(self):
        url = f'{self.__config['API_BASE_URL']}/view-content/{self.__config['DEFAULT_LANGUAGE']}/login/'

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                labels = data.get("labels", {})
                self.__update_view_labels(labels)
                return labels
            except httpx.HTTPStatusError as err:
                self.__view.display_error(err)

    async def login(self, login, password):
        url = f'{self.__config['API_BASE_URL']}/login/'
        payload = {'login': login, 'password': password}

        async with AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                token = response.json().get('token', None)
                self.__on_login_success(token)
            except HTTPStatusError:
                message = self.__labels.get('invalid_credentials', {}).get('value', '')
                self.__on_login_failure(message)

    @mainthread
    def __update_view_labels(self, labels):
        self.__view.set_labels(labels)

    @mainthread
    def __on_login_success(self, token):
        self.__app.token_model.token(token)
        self.__app.switch_to_data_table()

    @mainthread
    def __on_login_failure(self, message):
        self.__view.display_error(message)
