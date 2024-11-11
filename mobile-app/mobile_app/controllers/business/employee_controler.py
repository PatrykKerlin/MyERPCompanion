from httpx import AsyncClient, HTTPStatusError
from kivy.clock import mainthread


class EmployeeController:
    def __init__(self, view, config, token):
        self.__view = view
        self.__config = config
        self.__token = token
        self.__labels = self.__fetch_labels()

    async def __fetch_labels(self):
        url = f'{self.__config['API_BASE_URL']}/view-content/{self.__config['DEFAULT_LANGUAGE']}/all-employees/'

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

    async def fetch_data(self):
        url = f'{self.__config['API_BASE_URL']}/employee/'
        headers = {'Authorization': f'Token {self.__token}'}

        async with AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = await response.json()
                self.__update_table(data)
            except HTTPStatusError as err:
                self.__view.display_error(err)

    @mainthread
    def __update_view_labels(self, labels):
        self.__view.set_labels(labels)

    @mainthread
    def __update_table(self, data):
        self.__view.update_table(data)
