from django.shortcuts import redirect
from django.conf import settings
from django.views import View
from django.http import Http404

from ...helpers.constants import ApiEndpoints, SessionContent, PageNames
from ...helpers.api_client import ApiClient


class EntryPointView(View):
    def get(self, request):
        if not request.session.get(SessionContent.PAGES_DICT, None):

            api_url = settings.API_URL + ApiEndpoints.PAGE_PUBLIC
            response = ApiClient.get(api_url)

            if response.status_code != 200:
                raise Http404()

            pages = response.json()
            pages_dict = {page['name']: page for page in pages}
            request.session[SessionContent.PAGES_DICT] = pages_dict

        return redirect(PageNames.USER_LOGIN)
