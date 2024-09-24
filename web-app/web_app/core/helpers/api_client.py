import requests

from .constants import SessionContent


class ApiClient:
    @staticmethod
    def __get_headers(token=None):
        if token:
            return {'Authorization': f'Token {token}'}
        return None

    @staticmethod
    def get(url, token=None):
        headers = ApiClient.__get_headers(token)
        return requests.get(url, headers=headers)

    @staticmethod
    def post(url, json, token=None):
        headers = ApiClient.__get_headers(token)
        return requests.post(url, json=json, headers=headers)

    @staticmethod
    def put(url, json, token=None):
        headers = ApiClient.__get_headers(token)
        return requests.put(url, json=json, headers=headers)

    @staticmethod
    def patch(url, json, token=None):
        headers = ApiClient.__get_headers(token)
        return requests.patch(url, json=json, headers=headers)

    @staticmethod
    def delete(url, token=None):
        headers = ApiClient.__get_headers(token)
        return requests.delete(url, headers=headers)
