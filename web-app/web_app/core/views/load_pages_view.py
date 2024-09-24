from django.shortcuts import redirect
from django.conf import settings
from django.views import View
import requests


class LoadPagesView(View):
    def get(self, request):
        if not request.session.get('pages_data'):
            api_url = f'{settings.API_URL}/core/page-public/'
            response = requests.get(api_url)

            if response.status_code == 200:
                pages_data = response.json()
                pages_data_dict = {page['name']: page for page in pages_data}
                request.session['pages_data'] = pages_data_dict

        user_login_page = request.session.get('pages_data').get('user-login')

        if user_login_page:
            return redirect(user_login_page['name'])
