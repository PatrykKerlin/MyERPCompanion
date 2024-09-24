from django.shortcuts import redirect
from django.conf import settings
from django.views import View

from ...helpers.constants import ApiEndpoints, SessionContent
from ...helpers.api_client import ApiClient


class EntryPointView(View):
    def get(self, request):
        if not request.session.get(SessionContent.PAGES_DATA, None):
            api_url = settings.API_URL + ApiEndpoints.PAGE_PUBLIC
            response = ApiClient.get(api_url)

            if response.status_code == 200:
                pages_data = response.json()
                pages_data_dict = {page['name']: page for page in pages_data}
                request.session[SessionContent.PAGES_DATA] = pages_data_dict

        user_login_page = request.session.get(SessionContent.PAGES_DATA).get('user-login', None)

        if user_login_page:
            return redirect(user_login_page['name'])
