from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import Http404

from base.views.base_view import BaseView
from ..helpers.session import Session
from ..helpers.constants import ApiEndpoints, SessionContent, PageNames
from ..helpers.api_client import ApiClient


class LoginView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, page_name=PageNames.LOGIN, *args, **kwargs)

    def get(self, request):
        return render(request, self.context['page']['template'], self.context)

    def post(self, request):
        if not LoginView.__get_token(request):
            raise Http404()

        if not LoginView.__get_current_user(request):
            raise Http404()

        if not LoginView.__get_menu_content(request):
            raise Http404()

        return redirect(PageNames.INDEX)

    @staticmethod
    def __get_token(request):
        login = request.POST.get('login')
        password = request.POST.get('password')

        url = settings.API_URL + ApiEndpoints.TOKEN
        payload = {
            'login': login,
            'password': password
        }
        response = ApiClient.post(url, json=payload)

        if response.status_code != 200:
            return False

        token = response.json().get('token', '')
        Session.add(request, SessionContent.TOKEN, token)

        return True

    @staticmethod
    def __get_current_user(request):
        token = Session.get(request, SessionContent.TOKEN)
        url = settings.API_URL + ApiEndpoints.CURRENT_USER
        response = ApiClient.get(url, token)

        if response.status_code != 200:
            return False

        user = response.json()
        Session.add(request, SessionContent.CURRENT_USER, user)

        return True

    @staticmethod
    def __get_menu_content(request):
        token = Session.get(request, SessionContent.TOKEN)
        language = Session.get(request, SessionContent.CURRENT_USER)['language']
        url = f'{settings.API_URL}{ApiEndpoints.MENU_CONTENT}{language}/'
        response = ApiClient.get(url, token)

        if response.status_code != 200:
            return False

        menu_content = response.json()
        Session.add(request, SessionContent.MENU_CONTENT, menu_content)

        return True
