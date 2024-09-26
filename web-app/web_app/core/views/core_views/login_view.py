from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import Http404

from ..abstract_views.base_view import BaseView
from ...helpers.constants import ApiEndpoints, SessionContent, PageNames
from ...helpers.api_client import ApiClient


class LoginView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, page_name=PageNames.USER_LOGIN, current_user=False, *args, **kwargs)

    def get(self, request):
        return render(request, self.page['template'], self.context)

    def post(self, request):
        login = request.POST.get('login')
        password = request.POST.get('password')

        api_token_url = settings.API_URL + ApiEndpoints.TOKEN
        token_data = {
            'login': login,
            'password': password
        }
        token_response = ApiClient.post(api_token_url, json=token_data)

        if token_response.status_code != 200:
            raise Http404()

        token = token_response.json().get('token')
        request.session[SessionContent.TOKEN] = token

        user_api_url = settings.API_URL + ApiEndpoints.CURRENT_USER
        user_response = ApiClient.get(user_api_url, token)

        if user_response.status_code != 200:
            raise Http404()

        user = user_response.json()
        request.session[SessionContent.CURRENT_USER] = user

        return redirect(PageNames.INDEX)
