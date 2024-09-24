from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import Http404
import requests


class LoginView(View):
    def __init__(self):
        super().__init__()
        self.template = None

    def dispatch(self, request, *args, **kwargs):
        pages_data = request.session.get('pages_data', {})
        page = pages_data.get('user-login', None)

        if page:
            self.template = page.get('template')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        login = request.POST.get('login')
        password = request.POST.get('password')

        api_token_url = f'{settings.API_URL}/core/token/'
        token_data = {
            'login': login,
            'password': password
        }
        token_response = requests.post(api_token_url, data=token_data)

        if token_response.status_code == 200:
            token = token_response.json().get('token')
            request.session['token'] = token

            user_api_url = f'{settings.API_URL}/core/current-user/'
            headers = {'Authorization': f'Token {request.session['token']}'}
            user_response = requests.get(user_api_url, headers=headers)
            if user_response.status_code == 200:
                user = user_response.json()
                request.session['user'] = user

        user_login_page = request.session.get('pages_data').get('user-login')
        context = {'token': request.session['token'],
                   'user': request.session['user']}

        if user_login_page:
            return render(request, user_login_page['template'], context)
