from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404

from ...helpers.constants import ApiEndpoints, SessionContent, PageNames
from ...helpers.api_client import ApiClient


class BaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = None
        self.context = None

    def dispatch(self, request, *args, **kwargs):
        page_name = kwargs.pop('page_name', None)
        current_user = kwargs.pop('current_user', True)

        if current_user:
            if not request.session.get(SessionContent.CURRENT_USER, None):
                return redirect(ApiEndpoints.LOGIN)

        pages = request.session.get(SessionContent.PAGES_DICT, None)

        if not pages:
            return redirect(PageNames.ENTRY_POINT)

        self.page = pages.get(page_name, None)

        if not self.page:
            raise Http404()

        context_by_page = request.session.get(SessionContent.CONTEXT_BY_PAGE, {})
        self.context = context_by_page.get(page_name, None)

        if not self.context:
            page_content_url = f'{settings.API_URL}{ApiEndpoints.CONTENT_BY_PAGE}{self.page.get('id')}/'
            response = ApiClient.get(page_content_url)

            if response.status_code != 200:
                raise Http404()

            content = response.json()
            self.context = {content['key']: content['value'] for content in content}
            self.context['page_title'] = self.page.get('title')

            context_by_page[page_name] = self.context
            request.session[SessionContent.CONTEXT_BY_PAGE] = context_by_page

        return super().dispatch(request, *args, **kwargs)
