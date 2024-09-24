from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import Http404

from ...helpers.constants import ApiEndpoints, SessionContent
from ...helpers.api_client import ApiClient


class LoginView(View):
    def __init__(self):
        super().__init__()
        self.template = None

    def dispatch(self, request, *args, **kwargs):
        pages_data = request.session.get(SessionContent.PAGES_DATA, {})
        page = pages_data.get('user-login', None)

        if page:
            self.template = page.get('template')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        login = request.POST.get('login')
        password = request.POST.get('password')

        api_token_url = settings.API_URL + ApiEndpoints.TOKEN
        token_data = {
            'login': login,
            'password': password
        }
        # token_response = requests.post(api_token_url, data=token_data)
        token_response = ApiClient.post(api_token_url, json=token_data)

        if token_response.status_code == 200:
            token = token_response.json().get('token')
            request.session[SessionContent.TOKEN] = token

            user_api_url = settings.API_URL + ApiEndpoints.CURRENT_USER
            # headers = {'Authorization': f'Token {request.session[SessionContent.TOKEN]}'}
            # user_response = requests.get(user_api_url, headers=headers)
            user_response = ApiClient.get(user_api_url, token)
            if user_response.status_code == 200:
                user = user_response.json()
                request.session[SessionContent.CURRENT_USER] = user

        user_login_page = request.session.get(SessionContent.PAGES_DATA).get('user-login')
        context = {'token': request.session[SessionContent.TOKEN],
                   'user': request.session[SessionContent.CURRENT_USER]}

        if user_login_page:
            return render(request, user_login_page['template'], context)
