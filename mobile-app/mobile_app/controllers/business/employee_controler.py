import httpx
from httpx import AsyncClient, HTTPStatusError
from kivy.clock import mainthread


class EmployeeController:
    def __init__(self, view, config):
        self.__view = view
        self.__config = config

    async def fetch_labels(self, token):
        url = self.__config['API_BASE_URL'] + '/view-content/' + self.__config['DEFAULT_LANGUAGE'] + '/all_employees/'
        headers = {'Authorization': f'Token {token}'}

        async with AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                labels = data.get('labels', {})
                self.__update_view_labels(labels)
            except HTTPStatusError as err:
                self.__view.display_error(f'Error: {err}')

    async def fetch_data(self, token):
        url = self.__config['API_BASE_URL'] + '/employee/'
        headers = {'Authorization': f'Token {token}'}

        async with AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                self.__update_table(data)
            except HTTPStatusError as err:
                self.__view.display_error(f'Error: {err}')

    @mainthread
    def __update_view_labels(self, labels):
        self.__view.set_data_table(labels)

    @mainthread
    def __update_table(self, data):
        self.__view.update_table(data)
