from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404

from core.helpers.constants import ApiEndpoints, SessionContent, PageNames, Defaults
from core.helpers.api_client import ApiClient


class BaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = None

    def dispatch(self, request, *args, **kwargs):
        page_name = kwargs.pop('page_name', None)

        if not page_name:
            raise Http404()

        current_user = request.session.get(SessionContent.CURRENT_USER, {})

        if not current_user and page_name != PageNames.LOGIN:
            return redirect(PageNames.LOGIN)

        menu_content = request.session.get(SessionContent.MENU_CONTENT, {})

        if not menu_content and page_name != PageNames.LOGIN:
            return redirect(PageNames.LOGIN)

        user_language = current_user.get('language', Defaults.LANGUAGE)
        user_theme = current_user.get('theme', Defaults.THEME)

        pages = request.session.get(SessionContent.PAGES, {})
        current_page = pages.get(page_name, {})
        current_page_language = current_page.get('language', Defaults.LANGUAGE)
        current_page_theme = current_page.get('theme', Defaults.THEME)

        if not current_page or user_language != current_page_language:
            page_content_url = f'{settings.API_URL}{ApiEndpoints.PAGE_CONTENT}{user_language}/{page_name}/'

            token = request.session.get(SessionContent.TOKEN, '')

            if not token:
                response = ApiClient.get(page_content_url)
            else:
                response = ApiClient.get(page_content_url, token=token)

            if response.status_code != 200:
                raise Http404()

            current_page = response.json()
            pages[page_name] = current_page
            request.session[SessionContent.PAGES] = pages
            request.session.modified = True
        elif user_theme != current_page_theme:
            current_page['theme'] = user_theme
            pages[page_name] = current_page
            request.session[SessionContent.PAGES] = pages
            request.session.modified = True

        self.context = {
            'page': current_page,
            'menu': menu_content
        }
        return super().dispatch(request, *args, **kwargs)
